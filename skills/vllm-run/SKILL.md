---
name: vllm-run
description: vLLM/vLLM-Ascend model running, including offline and online inference
argument-hint: "run / inference / serve / offline / online"
---

# vLLM/vLLM-Ascend Model Running

> **Note**: Before running, use `npu-smi info` to check available NPU and set `ASCEND_RT_VISIBLE_DEVICES` environment variable.

## Debug Steps

1. Use offline inference (single-operator mode): `--enforce-eager`
1. After single operator mode work, try graph mode
1. if offline inference work, provide a online inference command for user.
