---
name: ascend
description: Entry point for Ascend inference toolchain, including vLLM-Ascend, msmodelslim quantization, and NPU debugging.
argument-hint: "vllm issue / quantization / npu usage"
---

# Ascend Inference Toolchain

This skill manages Ascend NPU-related tasks, troubleshooting, and toolchain usage.

## Current NPU Status
!`npu-smi info`

## Task Specifics

For detailed instructions on specific tools, refer to:

- **vLLM-Ascend**: See [vllm-install.md](vllm-install.md) for installation and [vllm-run.md](vllm-run.md) for running and troubleshooting.
- **msmodelslim**: 
    - [msmodelslim.md](msmodelslim.md) for the **Execution Protocol**.
    - [msmodelslim_ref.md](msmodelslim_ref.md) for **Technical Reference** (Naming, Config, MoE strategies).
    - [msmodelslim-tune/msmodelslim-tune.md](msmodelslim-tune/msmodelslim-tune.md) for auto precision tuning.

## Core Tips

- **Visible Devices**: Use `ASCEND_RT_VISIBLE_DEVICES=0,1` to isolate NPUs.
- **Source Debugging**: Use `pip show <package>` to find the editable source location for deep debugging.
