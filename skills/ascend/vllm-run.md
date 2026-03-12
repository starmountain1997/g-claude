# vLLM-Ascend Running & Troubleshooting

Guide for running and debugging vLLM on Ascend NPUs. This guide is modular; jump to the phase that matches your current progress.

**Pre-run check**: Always verify available devices with `npu-smi info`.

## Phase 1: Setup & Basic Validation
*Use this if you are starting with a new model or new environment.*

<Steps>
  <Step title="Locate Weights">
    Always ask the user for the local path to the model weights before proceeding.
  </Step>

  <Step title="Offline Validation">
    Create a standalone Python script for offline inference first to ensure the basic setup is functional.
  </Step>

  <Step title="Quantized Model Check">
    If the model is quantized, add `--quantization ascend` to all commands to use Ascend-specific quantization kernels.
  </Step>
</Steps>

## Phase 2: Compatibility & Debugging (Eager Mode)
*Use this if the model fails to run or produces errors in graph mode.*

<Steps>
  <Step title="Enable Eager Mode">
    Initially run with `--enforce-eager` to verify operator compatibility and isolate kernel issues.
  </Step>

  <Step title="Source-level Fix">
    If errors occur (e.g., missing kernels, assertion failures), create a new fix branch in the `vllm-ascend` directory and modify the source code directly. Re-run validation after each modification.
  </Step>
</Steps>

## Phase 3: Performance Optimization
*Use this if you already have a working script (e.g., in eager mode) and want to improve throughput.*

<Steps>
  <Step title="Disable Eager Mode">
    Once eager mode passes, remove `--enforce-eager` to enable graph mode for better performance.
  </Step>

  <Step title="Determine Parallelism">
    Read the `vllm-ascend` source code to determine the supported `tensor-parallel` (`--tp`) and `pipeline-parallel` (`--pp`) parameters for the target model architecture.
  </Step>

  <Step title="Graph Mode Selection">
    Read the source code to determine optimal graph mode parameters (e.g., `--block-size`, `--max-model-len`).
  </Step>

  <Step title="Memory Management">
    Adjust `--gpu-memory-utilization` based on NPU memory reported by `npu-smi`.
  </Step>

  <Step title="Further Tuning">
    Refer to the official docs for additional performance flags.
  </Step>
</Steps>

## Phase 4: Online Serving
*Use this once offline inference is stable and optimized.*

<Steps>
  <Step title="API Server Conversion">
    Convert the validated offline parameters into a `python -m vllm.entrypoints.openai.api_server` command.
  </Step>

  <Step title="Final Deployment">
    Ask the user for their preferred `model-served-name` and `port` before providing the final command. Add `--quantization ascend` if the model is quantized.
  </Step>
</Steps>
