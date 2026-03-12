# msmodelslim Quantization Protocol

Strict sequential protocol for model quantization, structural consultation, or debugging on Ascend NPUs.

## Pre-execution Validation

Verify hardware and software dependencies:
- `!pip show msmodelslim torch_npu transformers`

## Quantization Strategy Selection

### 1. One-Click Quantization
- **Discovery**: `msmodelslim quant -h`.
- **Save Directory**: Default to `/home/model_weights`.
- **Lifecycle**: Once initialization is confirmed, output the exact command and instruct the user to run it in their terminal. Kill any background process immediately once the main loop starts.

### 2. Custom Python Script
Fallback if "No best practice found" or specific requirements occur.

- **Act Method**: Default to `3` (Auto-mixed).
- **Anti Method**: Default to `m2` (Enhanced SmoothQuant).
- **Sensitive Layer Analysis**: 
  ```bash
  msmodelslim analyze --model_type <TYPE> --model_path <PATH> --metrics kurtosis --topk 15 --device npu
  ```
  Extract results to populate `disable_names`.

## OOM & Hardware

- **No CPU Quantization**: Always use NPU for `msmodelslim` operations.
- **Multi-NPU**: Implement if OOM occurs on a single device.
