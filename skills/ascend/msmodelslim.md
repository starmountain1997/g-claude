# msmodelslim Quantization Protocol

Strict sequential protocol for model quantization, structural consultation, or debugging on Ascend NPUs. This protocol ensures high-performance inference while maintaining model accuracy through systematic strategy selection.

## 1. Pre-execution Validation

Before starting any quantization task, verify that the environment and hardware are ready.

### Environment Check
Verify mandatory dependencies:
- `!pip show msmodelslim torch_npu transformers`

### Hardware Status
Ensure NPUs are available and not currently locked by other processes:
- `!npu-smi info`

---

## 2. Quantization Strategy Selection

Follow this hierarchy to select the most efficient quantization path:

### Strategy A: One-Click Quantization (Recommended)
**Best for**: Established models with existing best-practice configurations.
- **Best Practice Library**: Refer to `msmodelslim/lab_practice` for pre-configured YAML files.
- **Workflow**: 
  1. Discovery: `msmodelslim quant -h`
  2. Execution: Call `msmodelslim quant` with a specific YAML config.
  3. Default Save Directory: `/home/model_weights`.
- **Note**: If a custom YAML is provided by the user, prioritize it over library defaults.

### Strategy B: Sensitive Layer Analysis (Accuracy Priority)
**Best for**: Models experiencing significant accuracy drops or requiring custom precision tuning.
- **Analysis Command**:
  ```bash
  msmodelslim analyze --model_type <TYPE> --model_path <PATH> --metrics kurtosis --topk 15 --device npu
  ```
- **Action**: Extract the top results from the analysis to populate the `disable_names` list in your quantization configuration to prevent quantizing sensitive layers.
- **Defaults**:
  - `Act Method`: Default to `3` (Auto-mixed).
  - `Anti Method`: Default to `m2` (Enhanced SmoothQuant).

### Strategy C: Traditional Low-Level Quantization
**Best for**: Deep debugging or research requiring granular control.
- **Implementation**: Refer to the `example` directory within the `msmodelslim` source code for Python API usage patterns.

---

## 3. Hardware & Resource Management

### NPU Mandatory
- **No CPU Quantization**: `msmodelslim` operations **must** run on Ascend NPUs.
- **Multi-NPU Strategy**: If Out-of-Memory (OOM) occurs on a single device, distribute the process across multiple NPUs:
  ```bash
  export ASCEND_RT_VISIBLE_DEVICES=0,1,2,3
  ```

### Lifecycle Management
- Once a quantization command is initialized and confirmed, output the exact command for the user to run in their terminal.
- **Safety**: Terminate any background processes immediately after the main quantization loop begins to prevent resource contention.

---

## 4. Troubleshooting & Common Pitfalls

- **Weights Path**: Always verify that the `--model_path` contains the correct weights format (e.g., Safetensors or Bin).
- **Library Version**: Ensure `msmodelslim` version matches the `CANN` version installed on the system.
- **Permission Errors**: Check write permissions for the `--save_path`.
