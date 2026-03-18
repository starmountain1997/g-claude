# msmodelslim Quantization Protocol (Execution)

Strict sequential protocol for executing model quantization or debugging on Ascend NPUs.

## 1. Pre-execution Validation

Before starting any quantization task, verify the environment and hardware.

### Environment Check

Verify mandatory dependencies:

- `!pip show msmodelslim torch_npu transformers`

### Hardware Status

Ensure NPUs are available:

- `!npu-smi info`

______________________________________________________________________

## 2. Quantization Strategy Selection

Follow this hierarchy to select the most efficient path:

### Strategy A: One-Click Quantization (Recommended)

**Best for**: Established models with existing best-practice configurations.

- **Library**: `msmodelslim/lab_practice` (inside the source code).
- **Workflow**:
  1. Discovery: `msmodelslim quant -h`
  1. Execution: `msmodelslim quant` with a specific YAML config.
- **Note**: If a custom YAML is provided, prioritize it.

### Strategy B: Sensitive Layer Analysis (Accuracy Priority)

**Best for**: Models with accuracy drops or requiring custom precision.

- **Analysis Command**:
  ```bash
  msmodelslim analyze --model_type <TYPE> --model_path <PATH> --metrics kurtosis --topk 15 --device npu
  ```
- **Action**: Use results to populate the `disable_names` list in your quantization configuration.
- **Defaults**: `Act Method: 3`, `Anti Method: m2`.

### Strategy C: Traditional Low-Level Quantization

**Best for**: Deep debugging or research.

- **Implementation**: Refer to the `example` directory in `msmodelslim` source.

______________________________________________________________________

## 3. Hardware & Resource Management

- **NPU Mandatory**: msmodelslim **must** run on Ascend NPUs.
- **OOM Prevention (7B+ Models)**:
  1. **Layer-wise**: Enabled by default in One-Click.
  1. **CPU Offload**: Set `--device cpu` (One-Click) only if NPU memory is strictly insufficient.
- **Multi-NPU**: Distribute across multiple NPUs:
  ```bash
  export ASCEND_RT_VISIBLE_DEVICES=0,1,2,3
  ```

______________________________________________________________________

## 4. Troubleshooting & Output

### Expected Output Structure

```
├── quant_model_description.json         # Metadata
├── quant_model_weight_w8a8.safetensors  # Quantized weights
└── ... (original model files copied)
```

### Common Checks

- **Weights**: Verify `--model_path` contains Safetensors/Bin.
- **Version**: `msmodelslim` version must match the installed `CANN`.
- **Permissions**: Check write access for `--save_path`.

______________________________________________________________________

## Additional Reference

For detailed configuration guides, naming rules, and expert MoE strategies, see [msmodelslim_ref.md](msmodelslim_ref.md).
