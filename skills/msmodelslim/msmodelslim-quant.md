# msmodelslim Quantization Protocol

> **Purpose: weight quantization — converts model weights to W4A8/W8A8/W4A4 etc. and writes a quantized checkpoint.**

Strict sequential protocol for model quantization, structural consultation, or debugging on Ascend NPUs.

> **Hard rule — execute the user's dtype, never override it.** Whatever dtype the user specifies, run it exactly. Do not substitute a different dtype because you believe the model would perform better at another setting. Your opinions about suitability are irrelevant until evaluation data proves otherwise. The only path to a different dtype is: quantize → serve → evaluate → fail → sensitivity analysis → fail again → ask the user.

## 0. End-to-End Iterative Workflow

Always follow this loop. Never skip evaluation before declaring success.

```
User specifies target dtype (e.g. w4a8, w8a8, w4a4)
         │
         ▼
[Step 1] Quantize with target dtype
         Use Strategy A (one-click) if a lab_practice config exists.
         Use Strategy C (custom YAML) otherwise.
         │
         ▼
[Step 2] Serve with /vllm (set quantization="ascend")
         │
         ▼
[Step 3] Evaluate accuracy with /aisbench (GSM8K)
         Threshold: ≤ 1 percentage point drop vs FP16 baseline.
         │
    ┌────┴────┐
    │ PASS    │ FAIL
    ▼         ▼
  Done   [Step 4] Sensitive layer analysis → add disable_names
                  Retry quantization with the SAME target dtype.
                  Re-evaluate (Step 2–3).
                  │
             ┌────┴────┐
             │ PASS    │ FAIL
             ▼         ▼
           Done   [Step 5] STOP. Inform the user that the target dtype
                           failed even after sensitivity analysis.
                           Ask explicitly: "Fall back to <next tier>?"
                           Only proceed with user confirmation.
                           Then restart from Step 1 with the confirmed dtype.
```

> **Always follow the user's specified dtype.** Never silently downgrade or substitute a different dtype at any step. If a fallback is needed, stop and ask.

> **Model path**: `--model_path` must point to a local directory. If the model is not yet downloaded, use `/vllm` (model-download guide) first to get `$MODEL_PATH`.

## 1. Pre-execution Validation

Before starting any quantization task, verify that the environment and hardware are ready.

### Environment Check

Verify mandatory dependencies:

- `pip show msmodelslim torch_npu transformers`

### Model Support Check

If the current `transformers` version does not support the target model:

1. Upgrade `transformers` to the latest version and re-check support.
1. If the latest version still does not support the model, stop and inform the user — quantization cannot proceed without upstream support.

### Hardware Status

Ensure NPUs are available and not currently locked by other processes:

- `npu-smi info`

______________________________________________________________________

## 2. Quantization Execution

### Step 1A: One-Click Quantization (Start Here)

Check `msmodelslim/lab_practice` for a pre-configured YAML matching the model + target dtype. If one exists, use it.

- **`--quant_type`**: auto-matches the best YAML from `lab_practice`. Values: `w4a8`, `w4a8c8`, `w8a8`, `w8a8s`, `w8a8c8`, `w8a16`, `w16a16s`.
- **`--config_path`**: use a specific YAML directly — takes priority over `--quant_type`. These two flags are mutually exclusive.
- **Always pass** `--trust_remote_code True` for models with custom architecture (Qwen3, DeepSeek, GLM, etc.).

```bash
# Option A1: auto-match from lab_practice
msmodelslim quant \
	--model_path ${MODEL_PATH} \
	--save_path ${SAVE_PATH} \
	--device npu \
	--model_type <ModelName> \
	--quant_type <TARGET_DTYPE> \
	--trust_remote_code True

# Option A2: explicit config (preferred when a custom YAML exists)
msmodelslim quant \
	--model_path ${MODEL_PATH} \
	--save_path ${SAVE_PATH} \
	--device npu \
	--model_type <ModelName> \
	--config_path /path/to/config.yaml \
	--trust_remote_code True
```

### Step 1B: Custom YAML (When No lab_practice Config Exists)

Use this for: MoE models with mixed precision, models with no existing best-practice config, or when the one-click result fails accuracy. Build a YAML config using the parameter guidance below.

### Step 1C: Traditional Low-Level API (Deep Debugging Only)

Refer to the `example/` directory in the `msmodelslim` source for Python API patterns. Use only for research or granular debugging.

______________________________________________________________________

### Step 4: Sensitive Layer Analysis (Accuracy Recovery Fallback)

Run this **only after** evaluation fails (Section 0, Step 4). Do **not** run preemptively.

See [msmodelslim-analysis.md](msmodelslim-analysis.md) for the full analysis workflow: command syntax, metric selection, output interpretation, and YAML strategies for adding `disable_names` or promoting layers to W8A8.

______________________________________________________________________

### Parameter Selection

#### 3.1 Activation Scope (`act.scope`) and `symmetric`

`symmetric` is **not a free choice** — it is determined by `scope`. This is a hardware constraint on Ascend NPU.

| `scope` | `symmetric` | Type | When to use |
| :----------- | :---------- | :------ | :------------------------------------------------------------------------------------------------------------------------------------- |
| `per_token` | **`true`** | Dynamic | Default for all LLM quantization — one scale per token at runtime. Use for everything unless you have a specific reason not to. |
| `per_tensor` | **`false`** | Static | Scale fixed at calibration time. Use only for attention layers when maximizing throughput over accuracy (e.g., Qwen3-Coder-480B attn). |
| `pd_mix` | **`false`** | Hybrid | `per_token` during prefill, `per_tensor` during decode. Use **only** when KV cache is also quantized (`w8a8c8`). |

**Decision rule**: Use `per_token + symmetric: true` unless you are building a throughput-optimized config or quantizing KV cache.

______________________________________________________________________

#### 3.2 Weight Scope (`weight.scope`)

| `scope` | When to use | Seen in |
| :---------------------------------- | :---------------------------------------------------------- | :------------------------------------------------------------------------------------ |
| `per_channel` | Everything — standard for W8A8 and all W4A8 in lab_practice | All official W4A8 configs (Qwen3-235B, Qwen3-Next, Qwen3-Coder-480B, DeepSeek, GLM-5) |
| `per_group` + `ext.group_size: 256` | Only W4A4 — when absolute minimum memory is required | Qwen3-32B W4A4 only |
| `per_tensor` | Never in production — not seen in any lab_practice config | — |

______________________________________________________________________

#### 3.3 Weight Method (`weight.method`)

Method is **fully determined** by dtype + scope combination:

| dtype | scope | method | Notes |
| :----- | :------------ | :---------- | :------------------------------------------------------------------------------------------------------------------------ |
| `int8` | `per_channel` | `minmax` | Standard for all W8A8. Fast and sufficient. |
| `int8` | `per_channel` | `autoround` | Higher accuracy W8A8 (used for attention in W4A4 configs). |
| `int4` | `per_channel` | `ssz` | **Standard for all W4A8 in lab_practice.** Iterative MSE optimization. |
| `int4` | `per_group` | `autoround` | W4A4 only. SSZ does not support `per_group`. |

**Do not mix**: `ssz` with `per_group`, `gptq` with MoE experts, `autoround` with `per_channel` for INT4.

**Extra parameters (`ext`).** Certain method + scope combinations require or accept additional fields under `ext:`:

| method / scope | `ext` field | Default | When required |
| :------------- | :---------- | :------ | :------------ |
| `ssz` (any) | `step` | `50` | Optional — lower (e.g. `10`) to trade accuracy for speed. |
| `per_group` (any method) | `group_size` | `256` | **Required** whenever `scope: "per_group"` is used. |
| `gptq` (any) | `percdamp` | `0.01` | Optional — damping coefficient for Hessian smoothing. |
| `gptq` (any) | `block_size` | `128` | Optional — iteration block size. |

```yaml
# SSZ with reduced iterations
weight: {scope: "per_channel", dtype: "int4", symmetric: true, method: "ssz", ext: {step: 10}}

# per_group — group_size is mandatory
weight: {scope: "per_group", dtype: "int4", symmetric: true, method: "autoround", ext: {group_size: 256}}
```

______________________________________________________________________

#### 3.4 Outlier Suppression Preprocessor

Must run **before** `linear_quant`. Choose based on quantization aggressiveness and model type:

| Preprocessor | Use when | Typical subgraph types |
| :---------------------------------------------- | :------------------------------------------------------- | :------------------------------------------------------------------------- |
| `iter_smooth` | Dense models, W8A8 | `norm-linear`, `linear-linear`, `ov`, `up-down` |
| `flex_smooth_quant` | MoE models, standard W4A8 | Start with `norm-linear`; add `ov` if model has cross-attn/value subgraphs |
| `quarot` → `flex_smooth_quant` | W4A4, or architecturally complex W4A8 (Qwen3-Coder-480B) | `quarot` has no subgraph config |
| `quarot` → `flex_awq_ssz` → `flex_smooth_quant` | Heaviest outlier models (GLM-5, DeepSeek-V3.2) | `flex_awq_ssz` on `up-down`; `flex_smooth_quant` on remaining |

**Subgraph type selection for `flex_smooth_quant`**:

- `norm-linear` — universal, covers post-norm → linear patterns. Always include.
- `ov` — add if the model has o_proj following v_proj (cross-attention/value patterns). E.g., DeepSeek MLA.
- `up-down` — add if outliers persist in gate/up → down MLP paths. E.g., GLM-5, some DeepSeek variants.

______________________________________________________________________

#### 3.5 Calibration Dataset (`dataset`)

| Dataset | Use for |
| :-------------------- | :--------------------------------------------------------------------- |
| `mix_calib.jsonl` | Default — general-purpose. Used when no `dataset:` field is specified. |
| `qwen3_cot.json` | Reasoning/CoT models at W8A8 (Qwen3, QwQ) |
| `qwen3_cot_w4a4.json` | Reasoning models at W4A4 or aggressive W4A8 |
| `autocodebench.jsonl` | Code models (Qwen3-Coder) |

##### 3.5.1 Multimodal Models: Dataset Requirements

**Built-in datasets are text-only.** `mix_calib.jsonl` and the Qwen3 CoT variants contain no image inputs, so they cannot activate vision encoders or cross-modal projection layers during calibration. Using a text-only dataset on a multimodal model silently under-calibrates the vision components, producing poor quantization quality for image-heavy tasks.

**Rule: Always supply a custom multimodal calibration dataset when quantizing a VLM (Vision-Language Model).**

**Dataset format.** Each line is a JSON object with a `messages` field following the standard chat schema. Images must be embedded as base64 data URIs (preferred for portability) or as accessible `http(s)://` URLs. The calibration set should cover the same modality mix as the model's intended workload.

```jsonl
{"messages": [{"role": "user", "content": [{"type": "text", "text": "描述图片中的内容"}, {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,<BASE64>"}}]}, {"role": "assistant", "content": "图片中..."}]}
{"messages": [{"role": "user", "content": [{"type": "text", "text": "What does the chart show?"}, {"type": "image_url", "image_url": {"url": "data:image/png;base64,<BASE64>"}}]}, {"role": "assistant", "content": "The chart shows..."}]}
```

Practical guidelines for the calibration set:

- **Size**: 64–256 samples is sufficient; more does not meaningfully improve calibration.
- **Diversity**: Include a mix of natural images, diagrams, screenshots, and text-heavy images that reflect real workload distribution.
- **Language**: Match the primary language(s) the model will serve in production.
- **Image resolution**: Use the same resolution (or closest pre-processing pipeline) that the model uses at inference time. Down-scaling to a different size introduces distribution mismatch.

**Specifying the custom dataset in YAML.** Set the `dataset` field to an absolute path:

```yaml
apiversion: modelslim_v1
metadata:
  config_id: qwen2_vl_7b_w4a8

# ... qconfig anchors ...

spec:
  process:
    # ...

dataset: /path/to/multimodal_calib.jsonl # absolute path required
```

**Vision component layer protection.** Vision encoders and vision-language projection layers are highly sensitive to quantization. The standard LLM-focused `flex_smooth_quant` preprocessors do **not** cover ViT-style subgraphs, so leave these components in BF16 unless you have evidence they tolerate quantization.

Common naming patterns to exclude (adjust to the actual model architecture):

| Component | Typical glob pattern | Action |
| :--------------------------------- | :--------------------------------------------------- | :------------------ |
| Vision encoder (ViT body) | `*visual*`, `*vision_model*`, `*image_encoder*` | Exclude — keep BF16 |
| Patch embedding | `*patch_embed*`, `*pos_embed*`, `*cls_token*` | Exclude — keep BF16 |
| Vision-language projection | `*visual_projection*`, `*mm_projector*`, `*vl_proj*` | Exclude or W8A16 |
| Cross-attention (to visual tokens) | `*cross_attn*` | Exclude or W8A8 |
| Language model backbone | `*language_model*`, `*model.layers.*` | Quantize normally |

Example YAML snippet for a VLM with a separate `visual_model` and `mm_projector`:

```yaml
spec:
  process:
    - type: "flex_smooth_quant"
      enable_subgraph_type: ['norm-linear']
      include:
        - '*language_model*'   # suppress outliers only in the LM backbone

    - type: "group"
      configs:
        # Vision components — keep at full precision
        - type: "linear_quant"
          qconfig: *default_w8a16
          include: ["*mm_projector*", "*visual_projection*"]

        # LM attention — W8A8 for accuracy
        - type: "linear_quant"
          qconfig: *default_w8a8_dynamic
          include: ["*language_model*self_attn*"]

        # LM MLP — W4A8 for memory savings
        - type: "linear_quant"
          qconfig: *default_w4a8_dynamic
          include: ["*language_model*mlp*"]
          exclude: ["*gate"]
```

> The vision encoder body itself (`*visual_model*`, `*image_encoder*`) should be fully excluded from all `linear_quant` entries — do not add it to any `include` pattern unless you have verified it tolerates quantization via sensitivity analysis.

**Sensitivity analysis for VLMs.** When running `msmodelslim analyze` after a failed evaluation, pass the **same multimodal dataset** that was used during quantization:

```bash
msmodelslim analyze \
	--model_path ${MODEL_PATH} \
	--device npu \
	--model_type <VLM_ModelName> \
	--metrics kurtosis \
	--topk 20 \
	--calib_dataset /path/to/multimodal_calib.jsonl \
	--trust_remote_code True 2>&1 | tee analyze_<model>.log
```

Using a text-only dataset here will produce artificially uniform sensitivity scores for vision-adjacent layers, making the output unreliable.

______________________________________________________________________

#### 3.6 Layer Protection

Protecting first/last layers from aggressive quantization prevents accuracy collapse. Patterns observed in lab_practice:

- **Qwen3-Coder-480B W4A8**: excludes first 5 + last 5 layers from expert W4A8 quantization
- **DeepSeek-R1-0528 W4A8**: last expert layer forced to W8A8 instead
- **GLM-5 W4A8**: entire last layer excluded
- **Universal**: `*gate` router layers are **never** quantized across all configs

**Rule of thumb**: Start without layer protection. If accuracy drops, add exclusions for the first 3–5 and last 3–5 transformer layers, or bump them to W8A8.

```yaml
# Exclude first/last N layers from W4A8 expert quantization
- type: "linear_quant"
  qconfig: *default_w4a8_dynamic
  include: ["*mlp.experts*"]
  exclude:
    - "model.layers.{0,1,2,3,4}.*"
    - "model.layers.{55,56,57,58,59}.*"  # adjust to model.num_hidden_layers - N

# OR: bump boundary layers to W8A8 instead of excluding
- type: "linear_quant"
  qconfig: *default_w8a8_dynamic
  include: ["model.layers.{0,1,2,3,4}.mlp.experts*", "model.layers.{55,56,57,58,59}.mlp.experts*"]
```

______________________________________________________________________

## 4. Mixed Quantization (Mix Quant)

Use the `group` processor to apply different qconfigs to different layer sets.

### Common MoE Strategy

- **Attention**: W8A8 dynamic — preserves accuracy on sensitive layers
- **Shared MLP**: W8A8 dynamic — better activation accuracy
- **Expert layers**: W4A8 `per_channel + ssz` — maximizes memory savings (dominant pattern in lab_practice)

### YAML Template

```yaml
apiversion: modelslim_v1
metadata:
  config_id: <model_name>_w4a8
  score: 90
  verified_model_types:
    - <ModelName>
  label:
    w_bit: 4
    a_bit: 8
    is_sparse: False
    kv_cache: False

# Reusable qconfig anchors
default_w8a8_dynamic: &default_w8a8_dynamic
  act: { scope: "per_token", dtype: "int8", symmetric: true, method: "minmax" }
  weight:
    { scope: "per_channel", dtype: "int8", symmetric: true, method: "minmax" }

default_w4a8_dynamic: &default_w4a8_dynamic
  act: { scope: "per_token", dtype: "int8", symmetric: true, method: "minmax" }
  weight:
    { scope: "per_channel", dtype: "int4", symmetric: true, method: "ssz" }

spec:
  process:
    # Step 1: Outlier suppression — see Section 3.4 for preprocessor and subgraph type selection
    - type: "flex_smooth_quant"
      enable_subgraph_type: ["norm-linear"]
      include:
        - "*"

    # Step 2: Mixed quantization group
    - type: "group"
      configs:
        - type: "linear_quant"
          qconfig: *default_w8a8_dynamic
          include: ["*self_attn*"]

        - type: "linear_quant"
          qconfig: *default_w8a8_dynamic
          include: ["*mlp*"]
          exclude: ["*gate", "*mlp.experts.*"]

        - type: "linear_quant"
          qconfig: *default_w4a8_dynamic
          include: ["*mlp.experts*"]

  save:
    - type: "ascendv1_saver"
      part_file_size: 4
```

### Layer Filter Rules

- `include` / `exclude` accept Glob wildcards (`*`, `?`, `[abc]`, `[!abc]`).
- `exclude` overrides `include` within the same entry.
- Always exclude `*gate` routers — they are never quantized in any lab_practice config.
- Filter by index: `"model.layers.{0,1,2,3,4}.*"` — see Section 3.6 for layer protection strategy.

______________________________________________________________________

## 5. Quick Reference: Common qconfig Patterns

```yaml
# W8A8 Static (throughput-first, e.g. attention layers)
act:    {scope: "per_tensor",  dtype: "int8", symmetric: false, method: "minmax"}
weight: {scope: "per_channel", dtype: "int8", symmetric: true,  method: "minmax"}

# W8A8 Dynamic (accuracy-first, standard for LLMs)
act:    {scope: "per_token",   dtype: "int8", symmetric: true,  method: "minmax"}
weight: {scope: "per_channel", dtype: "int8", symmetric: true,  method: "minmax"}

# W4A8 per_channel+ssz (standard for MoE experts — all official lab_practice W4A8 configs)
act:    {scope: "per_token",   dtype: "int8", symmetric: true, method: "minmax"}
weight: {scope: "per_channel", dtype: "int4", symmetric: true, method: "ssz"}

# W4A8 per_group+autoround (W4A4 only, or when per_group granularity is explicitly needed)
act:    {scope: "per_token",   dtype: "int8", symmetric: true, method: "minmax"}
weight: {scope: "per_group",   dtype: "int4", symmetric: true, method: "autoround", ext: {group_size: 256}}

# W8A8 pd_mix (only with KV cache quantization / w8a8c8)
act:    {scope: "pd_mix",      dtype: "int8", symmetric: false, method: "minmax"}
weight: {scope: "per_channel", dtype: "int8", symmetric: true,  method: "minmax"}
```

______________________________________________________________________

## 6. Hardware & Resource Management

### NPU Mandatory

- **No CPU Quantization**: `msmodelslim` operations **must** run on Ascend NPUs.
- **Multi-NPU Strategy**: If Out-of-Memory (OOM) occurs on a single device, distribute the process across multiple NPUs:
  ```bash
  export ASCEND_RT_VISIBLE_DEVICES=0,1,2,3
  # then pass --device npu:0,1,2,3 to enable distributed layer-by-layer quantization
  ```

### Lifecycle Management

- **Safety**: Terminate any background processes immediately after the main quantization loop begins to prevent resource contention.

- **Artifact Storage**: Save all generated YAML configs and shell scripts to the current working directory. Do not save them elsewhere.

______________________________________________________________________

## 7. Troubleshooting & Common Pitfalls

- **Weights Path**: Always verify that the `--model_path` contains the correct weights format (e.g., Safetensors or Bin).
- **Library Version**: Ensure `msmodelslim` version matches the `CANN` version installed on the system.
- **Permission Errors**: Check write permissions for the `--save_path`.
- **Missing `trust_remote_code`**: Models with custom architectures (Qwen3, DeepSeek, etc.) will fail silently — always pass `--trust_remote_code True`.
- **`--quant_type` + `--config_path` conflict**: These two flags are mutually exclusive; use one or the other.
- **SSZ on per_group**: SSZ does not support `per_group` scope — switch to `autoround`.
- **Symmetric mismatch**: Ascend NPU hardware acceleration requires `symmetric: true` for all activation configs.
- **MoE + GPTQ**: GPTQ is not recommended for MoE expert layers — use `ssz` (per_channel) or `autoround` (per_group) instead.

______________________________________________________________________

## 8. Adding a New Model Adapter

When a new model (e.g. a new Qwen variant, a different architecture, or a third-party model) needs to be quantized and no `lab_practice` config exists yet, register it under `third-party/msmodelslim/`.

### 8.1 Directory Layout

```
third-party/msmodelslim/
└── <model_name_or_family>/
    ├── qwen3_cot_w4a8.yaml        # best-practice YAML (one per dtype)
    ├── qwen3_cot_w8a8.yaml
    └── <auxiliary_files>...        # shell scripts, datasets, notebooks
```

- One YAML per target dtype (e.g. `w4a8`, `w8a8`, `w4a4`).
- File names follow the pattern `<purpose>_<dtype>.yaml` — same convention as `lab_practice`.
- If the model is a variant of an existing family (e.g. Qwen3-14B inherits from Qwen3-32B), copy the closest existing YAML as a starting point rather than writing from scratch.

### 8.2 Decision Flow: Start from Which Config?

```
Is there a lab_practice YAML for this exact model + dtype?
│
├─ YES  → use msmodelslim quant --config_path directly (Strategy A2)
│
└─ NO
    │
    ├─ Is there a sibling model in the same family (e.g. Qwen3-32B → Qwen3-14B)?
    │   │
    │   ├─ YES → copy the sibling YAML, update metadata.config_id and verified_model_types
    │   │
    │   └─ NO  → write a fresh YAML (see Section 8.3)
    │
    └─ Is the model a VLM (Vision-Language Model)?
        │
        ├─ YES → follow Section 3.5.1 for calibration dataset + layer exclusion patterns
        │
        └─ NO  → standard text-only YAML workflow
```

### 8.3 Writing a Fresh YAML (Minimum Required Fields)

```yaml
apiversion: modelslim_v1
metadata:
  config_id: <model_name>_<dtype> # unique identifier, e.g. qwen3_14b_w4a8
  score: 0 # unverified — set to 0 or leave out
  verified_model_types:
    - <ModelName> # exact transformers model type string
  label:
    w_bit: <4|8>
    a_bit: <4|8>
    is_sparse: False
    kv_cache: False

# Inline qconfig anchors (no external references)
w8a8: &w8a8
  act: { scope: "per_token", dtype: "int8", symmetric: true, method: "minmax" }
  weight:
    { scope: "per_channel", dtype: "int8", symmetric: true, method: "minmax" }

w4a8: &w4a8
  act: { scope: "per_token", dtype: "int8", symmetric: true, method: "minmax" }
  weight:
    { scope: "per_channel", dtype: "int4", symmetric: true, method: "ssz" }

spec:
  process:
    - type: "flex_smooth_quant"
      enable_subgraph_type: ["norm-linear"]
      include:
        - "*"

    - type: "group"
      configs:
        - type: "linear_quant"
          qconfig: *w8a8
          include: ["*self_attn*"]

        - type: "linear_quant"
          qconfig: *w8a8
          include: ["*mlp*"]
          exclude: ["*gate"]

        - type: "linear_quant"
          qconfig: *w4a8
          include: ["*mlp.experts*"] # MoE only; omit for dense models

  save:
    - type: "ascendv1_saver"
      part_file_size: 4
```

**Required fields:**

| Field | Value |
| :------------------------------ | :---------------------------------------------------------------------------------------------------------- |
| `metadata.config_id` | `<model_name>_<dtype>` — unique slug, no spaces |
| `metadata.verified_model_types` | Exact `<ModelName>` string as passed to `--model_type` |
| `metadata.label.w_bit / a_bit` | Match the dominant `dtype` in the qconfig group |
| `dataset` | **VLM only**: absolute path to multimodal JSONL. Omit for text-only models (defaults to `mix_calib.jsonl`). |
| `include / exclude` | Start simple (as above); add layer protection only after evaluation fails (see Section 3.6). |

### 8.4 VLM Adapter Checklist

If the new model is a Vision-Language Model, additionally:

- [ ] Prepare a multimodal calibration dataset (64–256 samples, base64 image URIs in `messages` format) — see Section 3.5.1.
- [ ] Add `dataset: /absolute/path/to/multimodal_calib.jsonl` under `spec:` (not under `process:`).
- [ ] Exclude vision components: add `include: ["*mm_projector*", "*visual_projection*"]` with a BF16 or W8A16 qconfig. Exclude `*visual_model*`, `*image_encoder*` entirely.
- [ ] Run the curl probe from `ais_bench.md` to verify the served model accepts image inputs before evaluating.
- [ ] Pass `--calib_dataset /path/to/multimodal_calib.jsonl` to `msmodelslim analyze` if accuracy recovery is needed.

### 8.5 Registering a Third-Party / Custom Model

For models that are not upstream in `lab_practice` (e.g. a fine-tuned derivative, a community model):

1. Create `third-party/msmodelslim/<my_model_family>/`.
1. Place the best-practice YAML there.
1. If there is a HuggingFace repo, note the `model_id` in a `README.md` alongside the YAML.
1. The YAML's `metadata.verified_model_types` list is the integration point — `msmodelslim quant --model_type <ModelName>` will match against it.
1. If the model type string is unknown, run:

```bash
python -c "from transformers import AutoConfig; c = AutoConfig.from_pretrained('<HF_REPO_OR_LOCAL_PATH>', trust_remote_code=True); print(c.model_type)"
```

to get the exact string.

### 8.6 Validation After Adding

After placing the YAML:

1. Confirm the file parses: `python -c "import yaml; yaml.safe_load(open('path/to.yaml'))"`.
1. Run a dry-run quantization with `--help` or a short-calibration subset to catch config errors early.
1. Proceed with the full E2E workflow (quantize → serve → evaluate) per Section 0.
