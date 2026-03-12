---
name: ascend
description: Entry point for Ascend inference toolchain, including vLLM-Ascend, msmodelslim quantization, and NPU debugging.
argument-hint: "vllm issue / quantization / npu usage"
allowed-tools: Bash(npu-smi *), Read, Glob, Grep
---

# Ascend Inference Toolchain

This skill manages Ascend NPU-related tasks, troubleshooting, and toolchain usage.

## Current NPU Status
!`npu-smi info`

## Task Specifics

For detailed instructions on specific tools, refer to:

- **vLLM-Ascend**: See [vllm.md](vllm.md) for installation and running (online/offline).
- **msmodelslim**: See [msmodelslim.md](msmodelslim.md) for the quantization protocol and sensitive layer analysis.

## Core Tips

- **Visible Devices**: Use `ASCEND_RT_VISIBLE_DEVICES=0,1` to isolate NPUs.
- **Source Debugging**: Use `pip show <package>` to find the editable source location for deep debugging.
