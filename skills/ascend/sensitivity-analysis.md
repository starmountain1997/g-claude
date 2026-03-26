# Sensitivity Analysis

Use `msmodelslim analyze` to identify which layers are most sensitive to quantization. Run this when a quantized model shows accuracy degradation compared to the FP32 baseline.

______________________________________________________________________

## 1. When to Run

- Quantized model accuracy drops beyond acceptable tolerance on target benchmarks
- Specific task types (math reasoning, code, long-context) degrade while others remain stable
- First/last layer protection did not resolve the issue

______________________________________________________________________

## 2. Command

```bash
msmodelslim analyze \
  --model_type <ModelName> \
  --model_path ${MODEL_PATH} \
  --device npu \
  --metrics kurtosis \
  --calib_dataset ${CALIB_DATASET} \
  --topk 15 \
  --trust_remote_code False
```

### Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--model_type` | str | **required** | Model architecture name (see support list below) |
| `--model_path` | str | **required** | Path to the original model; use absolute path |
| `--device` | str | `npu` | Target device: `npu` or `cpu` |
| `--metrics` | str | `kurtosis` | Sensitivity algorithm: `std`, `quantile`, `kurtosis`, `attention_mse` |
| `--calib_dataset` | str | `boolq.jsonl` | Path to calibration dataset (JSON or JSONL). Relative paths resolve under `lab_calib/`. **Must match the dataset used during quantization.** |
| `--topk` | int | `15` | Number of most-sensitive layers to report (recommended: 10–20). Actual output may exceed this if QKV layers are reported together. |
| `--pattern` | List[str] | `*` | Layer name patterns to analyze, space-separated, supports wildcards. Omit to analyze all layers. |
| `--trust_remote_code` | bool | `False` | Set `True` only for models that require files outside the `transformers` library (e.g. DeepSeek-V3 series). |

### Metric Selection

| Metric | Formula | Use When |
| :--- | :--- | :--- |
| `kurtosis` | `E[(X-μ)⁴]/σ⁴ - 3` | **Default.** Detects layers with peaked/concentrated activation distributions; best for fine-grained control |
| `std` | `max(\|max\|, \|min\|) / std` | Fast scan for regular quantization scenarios |
| `quantile` | `2·max_abs / 254 / (Q3−Q1)` | High-precision targets; robust when outliers skew `std` results |
| `attention_mse` | MSE between FP and INT attention output | Attention accuracy specifically degraded; **DeepSeek-V3/R1 series only** |

> **`attention_mse` requirement**: The model adapter must implement `AttentionMSEAnalysisInterface` (`get_attention_module_cls` and `get_attention_output_extractor`). Currently only supported for DeepSeek-V3/R1 variants.

### Narrowing Scope with `--pattern`

To limit analysis to specific module types, pass space-separated patterns:

```bash
msmodelslim analyze \
  --model_type Qwen3-32B \
  --model_path ${MODEL_PATH} \
  --pattern "*.down_proj*" "*.o_proj*" \
  --metrics kurtosis \
  --calib_dataset ${CALIB_DATASET}
```

> **`model_type` support**: `std`, `quantile`, and `kurtosis` support the same model types as ModelslimV1 quantization (see `config.ini → [ModelAdapter]`). `attention_mse` only supports DeepSeek-V3/R1 variants. Unsupported types trigger a warning and fall back to the default adapter.

______________________________________________________________________

## 3. Reading the Output

```
=== Layer Analysis Results (kurtosis method) ===
Patterns analyzed: ['*.down_proj*', '*.o_proj*']
Total layers analyzed: 128
Layer Sensitivity Scores (higher score = more sensitive to quantization):
  model.layers.14.mlp.down_proj     score=142.7
  model.layers.31.self_attn.o_proj  score=138.2
  model.layers.0.mlp.down_proj      score=131.9
  ...

=== YAML Format for quantization ===
exclude:
  - "model.layers.14.mlp.down_proj"
  - "model.layers.31.self_attn.o_proj"
  - "model.layers.0.mlp.down_proj"
  ...
=== End of YAML Format ===
```

**Interpreting scores**: Higher = more sensitive = higher risk of accuracy loss when quantized. Focus on the top 10–20 entries.

**QKV grouping**: If a QKV-related layer appears in the top-K, all three (Q, K, V) are printed together, so actual output count may exceed `--topk`.

**Cluster vs. scatter pattern**:

- Scores cluster around specific layer indices → protect those index ranges
- Scores scatter randomly across layers → protect by module type (e.g., all `down_proj`)

______________________________________________________________________

## 4. Applying Results to the Quantization Config

Choose a strategy based on how many layers are sensitive and the size of the accuracy gap.

### Strategy 1: Exclude Sensitive Layers (simplest)

Paste the YAML block directly into your config's `exclude` field. Excluded layers stay in FP16/BF16.

```yaml
- type: "linear_quant"
  qconfig: *default_w4a8_dynamic
  include: ["*"]
  exclude:
    - "model.layers.14.mlp.down_proj"
    - "model.layers.31.self_attn.o_proj"
    - "model.layers.0.mlp.down_proj"
```

**When to use**: Large accuracy gap; only a small number of layers flagged (< 5% of total).

**Cost**: Slight memory increase for layers retained in FP16.

______________________________________________________________________

### Strategy 2: Promote Sensitive Layers to Higher Precision (mixed precision)

Instead of a full FP16 fallback, demote sensitive layers from W4A8 → W8A8. Saves more memory than Strategy 1 while still recovering accuracy.

Use a `group` processor — the last matching entry wins for a given layer:

```yaml
- type: "group"
  configs:
    - type: "linear_quant"
      qconfig: *default_w4a8_dynamic
      include: ["*"]
      exclude: ["*gate"]

    - type: "linear_quant"
      qconfig: *default_w8a8_dynamic
      include:
        - "model.layers.14.mlp.down_proj"
        - "model.layers.31.self_attn.o_proj"
        - "model.layers.0.mlp.down_proj"
```

**When to use**: Many layers flagged (5–15%); pure exclusion wastes too much memory.

______________________________________________________________________

### Strategy 3: Pattern-Level Protection

If scores consistently cluster around a specific module type (e.g., all `down_proj` layers score high), protect the entire type rather than individual indices:

```yaml
exclude:
  - "*mlp.down_proj*"
  - "*self_attn.o_proj*"
```

Or promote them all to W8A8 within a `group` (same structure as Strategy 2, using wildcards in `include`).

______________________________________________________________________

## 5. Iterative Refinement

Sensitivity analysis is rarely a one-shot fix:

1. Run analysis → identify top-K sensitive layers
1. Apply Strategy 1, 2, or 3 → re-quantize
1. Evaluate accuracy on target benchmark (see [ais_bench.md](ais_bench.md))
1. If still degraded: increase `--topk` to protect more layers, or switch metric
1. If accuracy recovered but memory/speed is unacceptable: reduce the protected set

**Typical convergence**: 2–3 iterations.

**When to escalate**: If manual layer protection does not close the accuracy gap after 3 iterations, use `msmodelslim tune` with an `evaluation` block targeting your benchmark.

______________________________________________________________________

## 6. Common Patterns and Fixes

| Symptom | Likely Cause | Fix |
| :--- | :--- | :--- |
| Math/reasoning accuracy drops | First/last layers or `down_proj` outliers | Exclude or promote first 3 + last 3 layers |
| Attention-heavy tasks degrade | `o_proj` or `v_proj` sensitive | Run `--metrics attention_mse`, protect `*self_attn*` |
| MoE model: expert accuracy drops | Expert `down_proj` outliers | Protect boundary expert layers by index |
| All metrics show uniform sensitivity | Calibration dataset mismatch | Re-run with a domain-matched calibration set |
| High scores on `lm_head` only | Normal — always excluded | Verify `lm_head` is in `exclude` list |

______________________________________________________________________

## 7. Full Example: W4A8 Config with Sensitivity-Derived Exclusions

```yaml
apiversion: modelslim_v1
metadata:
  config_id: qwen3_32b_w4a8_sensitivity_tuned
  label:
    w_bit: 4
    a_bit: 8

default_w8a8_dynamic: &default_w8a8_dynamic
  act:    {scope: "per_token",   dtype: "int8", symmetric: true, method: "minmax"}
  weight: {scope: "per_channel", dtype: "int8", symmetric: true, method: "minmax"}

default_w4a8_dynamic: &default_w4a8_dynamic
  act:    {scope: "per_token",   dtype: "int8", symmetric: true, method: "minmax"}
  weight: {scope: "per_channel", dtype: "int4", symmetric: true, method: "ssz"}

spec:
  process:
    - type: "flex_smooth_quant"
      enable_subgraph_type: ['norm-linear']
      include: ['*']

    - type: "group"
      configs:
        - type: "linear_quant"
          qconfig: *default_w4a8_dynamic
          include: ["*"]
          exclude: ["*gate"]

        - type: "linear_quant"
          qconfig: *default_w8a8_dynamic
          include:
            # Paste top-K output from `msmodelslim analyze` here
            - "model.layers.14.mlp.down_proj"
            - "model.layers.31.self_attn.o_proj"
            - "model.layers.0.mlp.down_proj"

  save:
    - type: "ascendv1_saver"
      part_file_size: 4

dataset: mix_calib.jsonl
```
