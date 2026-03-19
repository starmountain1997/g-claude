# msmodelslim Quantization Protocol

Choose one of the two paths below to perform model quantization on Ascend NPUs.

## 1. Preparation

Verify hardware availability before starting:

- `npu-smi info`
- `pip show msmodelslim torch_npu transformers`

______________________________________________________________________

## 2. Execution Paths

### Path A: One-Click (Automatic)

**Best for**: Established models with existing best-practice configurations.

- **Best Practice Library**: Refer to `msmodelslim/lab_practice` for pre-configured YAML files.
- **Workflow**:
  1. Discovery: `msmodelslim quant -h`
  1. Execution: Use a pre-configured YAML from `msmodelslim/lab_practice`.
- **Default Save**: `/home/model_weights`.
- **Fallback**: If Path A fails (e.g., accuracy loss or configuration mismatch), proceed to Path B for manual tuning.

### Path B: Custom YAML (User-Defined)

**Best for**: Fine-grained control over per-layer strategy, mixed precision, or MoE models.

- **Reference**: Use existing YAML files in `msmodelslim/lab_practice` as a baseline for your custom configuration.
- **Action**: Run `msmodelslim quant --config <YOUR_YAML_PATH>`
- **Configuration Tips**:
  - **Quantization Method** (Scale Calculation):
    - `minmax`: Fast, uses global range. Best for **Weights**.
    - `ssz`: Optimized error search (ModelSlim specialty). Best for **Activation** (accuracy).
    - `kl`: Information entropy calibration. High accuracy, slow.
  - **Granularity (Weights)**:
    - Use `per_channel` by default for better precision.
    - In `per_group` mode, `group_size` must be one of: **`[32, 64, 128, 256]`**.
  - **Granularity (Activation)**:
    - Use `per_token` (dynamic) to prioritize **accuracy**.
    - Use `per_tensor` (static) to prioritize **performance**.
  - **Symmetry**: Use `symmetric=True` for most scenarios (especially W8A8 and W4A8) to balance performance and accuracy.
  - **Act Method**: Set to `3` (Auto-mixed) for balanced performance.
  - **Anti Method**: Set to `m2` (Enhanced SmoothQuant) to mitigate outliers.
  - **MoE Optimization** (DeepSeek/Qwen):
    - **Attention Module**: Use **W8A8** (`per_channel` weights, `per_token` activation) to preserve logic coherence.
    - **Expert Module**: Use **W4A8** (`per_group` weights, `per_token` activation) to save 80%+ memory and fit larger models on fewer NPUs.
    - **Performance**: Keep activation at **8-bit** (A8) to leverage native INT8 hardware acceleration.
  - **Summary**: Use `minmax` for weights; use `ssz` for activation to obtain better inference precision.
  - **Sensitive Layers**: If accuracy drops, run `msmodelslim analyze` to identify layers to add to your `disable_names` list.

______________________________________________________________________

## 3. Granularity Selection (Scope)

Source: `msmodelslim/ir/qal/qbase.py`

### Activation Scope (`act`)

| Scope | Type | Description | Use Case |
| :--- | :--- | :--- | :--- |
| `per_tensor` | Static | One scale computed at calibration, shared across all tokens | Throughput-first, INT8 baseline |
| `per_token` | Dynamic | Scale computed per token at inference time | Accuracy-first, recommended for LLMs |
| `pd_mix` | Hybrid | `per_token` during prefill, `per_tensor` during decode | Balance first-token latency and throughput |

### Weight Scope (`weight`)

| Scope | Description | Use Case |
| :--- | :--- | :--- |
| `per_channel` | Independent scale per output channel | Standard INT8 weight quantization |
| `per_group` | Independent scale per group; requires `ext.group_size` | INT4 weights, memory-constrained scenarios |
| `per_tensor` | Single scale for entire weight matrix | Lowest overhead, lowest accuracy |
| `per_block` | Block-wise quantization | MXFp8/MXFp4 formats only |

**Rules**:

- Activations on Ascend NPU **must** use `symmetric: true`.
- INT4 weights should use `per_group` with `group_size: 128` or `256`.
- `per_group` requires `method: "ssz"` or `method: "autoround"` (not `gptq`).

______________________________________________________________________

## 4. Calibration Method Selection

Source: `msmodelslim/core/quantizer/impl/`

### MinMax (`method: "minmax"`)

Computes scale from min/max of calibration data. Fastest, sensitive to outliers.

- **Use**: INT8 baseline, fast iteration, any scope.

### SSZ (`method: "ssz"`)

Iterative least-squares optimization (default 50 iterations), greedy MSE acceptance.

- **Use**: INT4 `per_channel` weights. Slightly slower than MinMax but better accuracy.
- **Limitation**: Requires `per_channel` scope; weight must be 2D tensor.
- **Config**: `ext.step` overrides iteration count.

### GPTQ (`method: "gptq"`)

Hessian-guided column-by-column weight quantization with error compensation.

- **Use**: Highest accuracy for `per_channel` / `per_group` INT8. Requires real calibration data.
- **Limitation**: Slow; not recommended for MoE expert layers.
- **Config**: `ext.percdamp` (default `0.01`), `ext.block_size` (default `128`).

### AutoRound (`method: "autoround"`)

Learns optimal rounding direction for quantized values.

- **Use**: Low-bit quantization (`per_group` INT4); comparable accuracy to GPTQ, faster.

### Method Selection Guide

| Method | Speed | Accuracy | Scope Constraint | Recommended For |
| :--- | :--- | :--- | :--- | :--- |
| `minmax` | Fastest | Baseline | All scopes | INT8, quick validation |
| `ssz` | Medium | Medium-High | `per_channel` only | INT4 per_channel |
| `gptq` | Slow | Highest | `per_channel`, `per_group` | Precision-critical INT8 |
| `autoround` | Medium | High | `per_group` | INT4 per_group, MoE experts |

______________________________________________________________________

## 5. Mixed Quantization (Mix Quant)

Use the `group` processor to apply different qconfigs to different layer sets.

### Common MoE Strategy

- **Attention**: W8A8 static — preserves coherence
- **Shared MLP**: W8A8 dynamic — better activation accuracy
- **Expert layers**: W4A8 per_group — maximizes memory savings

### YAML Template

```yaml
# Reusable qconfig anchors
default_w8a8: &default_w8a8
  weight: {scope: "per_channel", dtype: "int8", symmetric: true,  method: "minmax"}
  act:    {scope: "per_tensor",  dtype: "int8", symmetric: false, method: "minmax"}

default_w8a8_dynamic: &default_w8a8_dynamic
  weight: {scope: "per_channel", dtype: "int8", symmetric: true,  method: "minmax"}
  act:    {scope: "per_token",   dtype: "int8", symmetric: true,  method: "minmax"}

default_w4a8_dynamic: &default_w4a8_dynamic
  weight:
    scope: "per_group"
    dtype: "int4"
    symmetric: true
    method: "autoround"
    ext: {group_size: 256}
  act: {scope: "per_token", dtype: "int8", symmetric: true, method: "minmax"}

spec:
  process:
    # Step 1: Outlier suppression (before quantization)
    - type: "flex_smooth_quant"
      enable_subgraph_type: ['norm-linear', 'linear-linear', 'up-down']

    # Step 2: Mixed quantization group
    - type: "group"
      configs:
        - type: "linear_quant"
          qconfig: *default_w8a8
          include: ["*self_attn*"]
          exclude: ["*kv_b_proj"]

        - type: "linear_quant"
          qconfig: *default_w8a8_dynamic
          include: ["*mlp*"]
          exclude: ["*gate", "*mlp.experts.*"]

        - type: "linear_quant"
          qconfig: *default_w4a8_dynamic
          include: ["*mlp.experts*"]
          exclude: ["lm_head"]
```

### Layer Filter Rules

- `include` / `exclude` accept Glob wildcards (`*`, `?`, `[abc]`, `[!abc]`).
- `exclude` overrides `include` — use it to protect sensitive layers.
- Always exclude: `lm_head`, `gate`, first/last transformer layers to prevent accuracy collapse.
- Filter by index: `"model.layers.{0,1,2,3,4}.*"`

______________________________________________________________________

## 6. Quick Reference: Common qconfig Patterns

```yaml
# W8A8 Static (high throughput)
act:    {scope: "per_tensor",  dtype: "int8", symmetric: false, method: "minmax"}
weight: {scope: "per_channel", dtype: "int8", symmetric: true,  method: "minmax"}

# W8A8 Dynamic (high accuracy)
act:    {scope: "per_token",   dtype: "int8", symmetric: true,  method: "minmax"}
weight: {scope: "per_channel", dtype: "int8", symmetric: true,  method: "minmax"}

# W4A8 SSZ (low memory, per_channel only)
act:    {scope: "per_token",   dtype: "int8", symmetric: true, method: "minmax"}
weight: {scope: "per_channel", dtype: "int4", symmetric: true, method: "ssz"}

# W4A8 AutoRound (low memory, per_group)
act:    {scope: "per_token",   dtype: "int8", symmetric: true, method: "minmax"}
weight: {scope: "per_group",   dtype: "int4", symmetric: true, method: "autoround", ext: {group_size: 256}}
```

______________________________________________________________________

## 7. Hardware & Resource Management

- **Long-running Tasks**: If a quantization command is expected to take significant time, save it as a local `.sh` script and prompt the user to run it manually (e.g., via `nohup` or `screen`).
- **NPU Mandatory**: All quantization tasks **must** run on Ascend NPUs.
- **Multi-NPU**: If OOM occurs, set `export ASCEND_RT_VISIBLE_DEVICES=0,1,2,3`.
- **Weights Path**: Verify `--model_path` contains the correct weights format (Safetensors/Bin).
- **Permissions**: Ensure write access to the `--save_path`.
- **Lifecycle**: Once a quantization command is initialized, output the exact command for the user to run. Terminate background processes immediately after quantization begins.

______________________________________________________________________

## 8. Troubleshooting & Common Pitfalls

- **Weights Path**: Always verify that the `--model_path` contains the correct weights format (e.g., Safetensors or Bin).
- **Library Version**: Ensure `msmodelslim` version matches the `CANN` version installed on the system.
- **Permission Errors**: Check write permissions for the `--save_path`.
- **SSZ on per_group**: SSZ does not support `per_group` scope — switch to `autoround` or `gptq`.
- **Symmetric mismatch**: Ascend NPU hardware acceleration requires `symmetric: true` for all configs.
- **MoE + GPTQ**: GPTQ is not recommended for MoE expert layers — use `autoround` instead.
