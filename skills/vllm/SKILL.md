---
name: vllm
description: vLLM-Ascend serving toolchain. Use when installing vLLM on Ascend NPUs, running offline inference, launching a model as an OpenAI-compatible API server, tuning throughput/latency for a specific serving scenario, or contributing to the vllm-ascend project. Trigger whenever the user discusses vLLM deployment, vLLM errors, serving a model on Ascend, or wants to get inference running before evaluation.
argument-hint: install / run / serve / contribute
---

# vLLM-Ascend

Handles vLLM-Ascend installation, running, performance tuning, and contribution workflow.

## Prerequisites

Before any vLLM task:

1. **NPU hardware check** — use `/ascend` to verify NPUs are healthy and free (`npu-smi info`)
2. **Model on disk** — see [model-download.md](model-download.md). Never pass an online model ID to vLLM; always use a local path.

## Task Specifics

- **Installation**: [vllm-install.md](vllm-install.md) — version-pinning between `vllm` and `vllm-ascend`, editable install
- **Running & Tuning**: Always start with [scenario-inquiry.md](scenario-inquiry.md) to define performance goals, then follow [vllm-run.md](vllm-run.md) for offline validation → graph mode → online serving
- **Contributing**: [vllm-contribute.md](vllm-contribute.md) — DCO signature requirement, PR description template

## After Serving

Once the API server is up, use `/aisbench` to run accuracy or performance benchmarks against it.

## Core Tips

- All toolkits (`vllm`, `vllm-ascend`) are installed in editable mode. Run `pip show <package>` to find the source directory before modifying or referencing them.
- Before any debugging session, create a new git branch to isolate changes:
  ```bash
  git checkout -b debug/TOPIC
  ```
