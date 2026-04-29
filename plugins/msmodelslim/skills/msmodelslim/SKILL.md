---
name: msmodelslim
description: msmodelslim model quantization on Ascend NPUs. Use when quantizing LLMs or VLMs to W4A8, W8A8, W4A4, or other dtypes using msmodelslim. Covers one-click quantization, custom YAML configs, mixed quantization for MoE models, sensitive layer analysis, and adding new model adapters. Trigger whenever the user wants to compress a model, reduce memory footprint, or produce a quantized checkpoint for Ascend NPU serving.
argument-hint: quantize / analyze / new model
license: MIT
---

# msmodelslim

Handles model weight quantization on Ascend NPUs: from one-click configs to custom YAML, mixed precision, and accuracy recovery.

## Prerequisites

Before quantizing:

1. **NPU hardware check** — use `/ascend` to verify NPUs are healthy and free (`npu-smi info`)
1. **Model on disk** — use `/model-download` to get a local `$MODEL_PATH`. Never pass an online model ID.

## Task Specifics

- **Quantization protocol**: [msmodelslim-quant.md](msmodelslim-quant.md) — full E2E workflow, YAML config reference, mixed quantization, VLM support, troubleshooting
- **Sensitive layer analysis**: [msmodelslim-analysis.md](msmodelslim-analysis.md) — run only after evaluation fails; identifies layers to exclude or promote

## After Quantizing

The E2E loop is: quantize → serve → evaluate → (if fail) analyze → retry.

- **Serve the quantized model**: use `/vllm` with `quantization="ascend"` set in the LLM config
- **Evaluate accuracy**: use `/aisbench` (GSM8K; threshold ≤ 1 pp drop vs FP16 baseline)

## Run Commands via Shell Script

All quantization commands must be saved to a shell script and executed through it so output is captured in a timestamped log file. See the template in `/ascend` → "Common Requirement: Run via Shell Script with Log Output".

## Core Tips

- `msmodelslim` is installed in editable mode. Run `pip show msmodelslim` to find the source directory.
