# vLLM-Ascend Running & Troubleshooting

Guide for running and debugging vLLM on Ascend NPUs.

## Running & Troubleshooting

**Standard Workflow for New Models**:

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

  <Step title="Eager Mode (Debug)">
    Initially run with `--enforce-eager` to verify operator compatibility and isolate kernel issues.

    <Tip>
      **Source-level Fix**: If errors occur (e.g., missing kernels, assertion failures), create a new fix branch in the `vllm-ascend` directory and modify the source code directly. Re-run validation after each modification.
    </Tip>
  </Step>

  <Step title="Performance Optimization">
    Once eager mode passes, optimize for performance:

    - **Determine Parallelism**: First read the `vllm-ascend` source code to determine the supported `tensor-parallel` and `data-parallel` parameters for the target model architecture.
    - **Graph Mode Selection**: Read the source code to determine graph mode parameters

    - **Further Tuning**: Refer to the official docs for additional performance flags.
  </Step>

  <Step title="Online Serving">
    Convert the validated offline parameters into a `python -m vllm.entrypoints.openai.api_server` command. Add `--quantization ascend` if the model is quantized.

    <Warning>
      **Crucial**: Ask the user for their preferred `model-served-name` and `port` before providing the final command.
    </Warning>
  </Step>
</Steps>

**Pre-run check**: Always verify available devices with `npu-smi info`.
