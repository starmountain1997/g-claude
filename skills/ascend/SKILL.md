______________________________________________________________________

## name: ascend description: Entry point for Ascend NPU inference toolchain. Use when running vLLM on Ascend/NPU, quantizing models with msmodelslim, or debugging NPU errors. argument-hint: "vllm issue / quantization / npu usage"

# Ascend Inference Toolchain

This skill manages Ascend NPU-related tasks, troubleshooting, and toolchain usage.

## Current NPU Status

!`npu-smi info`

## Task Specifics

For detailed instructions on specific tools, refer to:

- **vLLM-Ascend**: See [vllm-install.md](vllm-install.md) for installation and [vllm-run.md](vllm-run.md) for running and troubleshooting.
- **msmodelslim**: See [msmodelslim.md](msmodelslim.md) for quantization protocols.

## Core Tips

- **Visible Devices**: Use `ASCEND_RT_VISIBLE_DEVICES=0,1` to isolate NPUs.
- **Source Debugging**: Use `pip show <package>` to find the editable source location for deep debugging.
