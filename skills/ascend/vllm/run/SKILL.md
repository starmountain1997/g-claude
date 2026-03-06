---
name: vllm-run
description: vLLM/vLLM-Ascend model running, including offline and online inference
argument-hint: "run / inference / serve / offline / online"
---

# vLLM/vLLM-Ascend Model Running

> **Note**: Before running, use `npu-smi info` to check available NPU and set `ASCEND_RT_VISIBLE_DEVICES` environment variable.

## Debug Steps

1. Use offline inference (single-operator mode): `--enforce-eager`
2. After offline inference works, try graph mode:
   - ACL Graph: enabled by default in V1 Engine, just don't set `--enforce-eager`
   - For parameter configuration, refer to `vllm-ascend/docs/source/user_guide/configuration/additional_config.md`

## Online Inference (provide only after confirming offline inference works)

```bash
vllm serve /path/to/model --enforce-eager
```
