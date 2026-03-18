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

- **Action**: Run `msmodelslim quant` using library defaults.
- **Workflow**:
  1. Discovery: `msmodelslim quant -h`
  1. Execution: Use a pre-configured YAML from `msmodelslim/lab_practice`.
- **Default Save**: `/home/model_weights`.
- **Fallback**: If Path A fails (e.g., accuracy loss or configuration mismatch), proceed to Path B for manual tuning.

### Path B: Custom YAML (User-Defined)

**Best for**: Manual control or specific tuning requirements.

- **Reference**: Use existing YAML files in `msmodelslim/lab_practice` as a baseline for your custom configuration.
- **Action**: Run `msmodelslim quant --config <YOUR_YAML_PATH>`
- **Configuration Tips**:
  - **Quantization Method** (Scale Calculation):
    - `minmax`: Fast, uses global range. Best for **Weights**.
    - `ssz`: Optimized error search (ModelSlim specialty). Best for **Activation** (accuracy).
    - `kl`: Information entropy calibration. High accuracy, slow.
  - **Granularity (Weights)**:
    ...
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

## 3. Hardware & Resource Management

- **NPU Mandatory**: All quantization tasks **must** run on Ascend NPUs.
- **Multi-NPU**: If OOM occurs, set `export ASCEND_RT_VISIBLE_DEVICES=0,1,2,3`.
- **Weights Path**: Verify `--model_path` contains the correct weights format (Safetensors/Bin).
- **Permissions**: Ensure write access to the `--save_path`.
