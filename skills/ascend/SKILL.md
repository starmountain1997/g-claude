---
name: ascend
description: Ascend inference toolchain debugging entry, covering vLLM and msmodelslim
argument-hint: "vllm-ascend runtime issue / msmodelslim quantization issue / npu usage"
---

Ascend inference toolchain debugging entry.

## Common Commands

Check NPU usage:
```bash
npu-smi info
```

> **Tip**: Before running NPU scripts, use `npu-smi info` to check available NPU. Use `ASCEND_RT_VISIBLE_DEVICES` environment variable to specify NPU devices:
> ```bash
> ASCEND_RT_VISIBLE_DEVICES=0,1 python script.py
> ```

## Source Code Location

1. Run `pip show <package>` to get `Editable project location` - this is the source directory
2. Check `docs/` in the source directory for documentation

## Sub-Skills

- **vllm** - vLLM/vLLM-Ascend source debugging and runtime issue troubleshooting
- **msmodelslim** - msmodelslim quantization tool debugging

Please describe the specific issue you are facing.
