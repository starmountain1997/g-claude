---
name: vllm
description: vLLM/vLLM-Ascend source debugging, locate and resolve issues by reading source code
disable-model-invocation: true
argument-hint: "vllm / vllm-ascend / source location / build error / runtime error"
---

vLLM/vLLM-Ascend source debugging.

> For NPU usage and source code location, see [ascend main skill](../SKILL.md).

## Sub-Skills

- **vllm-install** - vLLM/vLLM-Ascend source installation
- **vllm-run** - vLLM/vLLM-Ascend model running

## Issue Location

1. Run `pip show vllm-ascend` to get the source location
2. Use Grep/Read to explore the source code
