---
name: tensor-cast
description: TensorCast model-level performance analysis for Ascend NPUs. Use to analyze operator-level execution time, memory footprint, FLOPs, and computational characteristics of transformer models. Triggers when the user wants model analysis, FLOPs estimation, memory profiling, or operator breakdown.
license: MIT
---

# TensorCast

TensorCast intercepts a PyTorch program's computational graph and simulates its execution on a user-defined hardware configuration to predict performance without real hardware.

## When to Use

- Estimate operator-level execution time
- Analyze memory footprint (weights, KV cache, activations)
- Get FLOPs and computational characteristics
- Profile model before running on real hardware

## Quick Start

**Text generation simulation:**

```bash
MSMODELING_PATH=$(uv pip show liuren_modeling 2>/dev/null | grep "Editable project location:" | cut -d':' -f2 | tr -d ' ')
cd $MSMODELING_PATH

python -m cli.inference.text_generate Qwen/Qwen3-32B \
  --num-queries 2 \
  --query-length 3500 \
  --device TEST_DEVICE
```

**Video generation simulation:**

```bash
MSMODELING_PATH=$(uv pip show liuren_modeling 2>/dev/null | grep "Editable project location:" | cut -d':' -f2 | tr -d ' ')
cd $MSMODELING_PATH

# Requires a diffusers model directory with transformer/config.json and vae/config.json
python -m cli.inference.video_generate \
  /path/to/your/diffusers/model \
  --batch-size 1 \
  --seq-len 16 \
  --height 576 \
  --width 1024 \
  --frame-num 14 \
  --sample-step 25 \
  --device TEST_DEVICE
```

## Supported Models

Always check the latest supported matrix:

```bash
MSMODELING_PATH=$(uv pip show liuren_modeling 2>/dev/null | grep "Editable project location:" | cut -d':' -f2 | tr -d ' ')
cat $MSMODELING_PATH/docs/en/tensor_cast_instruct.md | grep -A 20 "Supported Matrix"
```

This lists supported:

- **Text model families** (Qwen3, GLM-4, DeepSeek V3, etc.)
- **Vision-language models** (Qwen3-VL, InternVL)
- **Video generation models** (Wan, HunyuanVideo)
- **Quantization types** (W8A16/W8A8/W4A8, FP8, MXFP4)
- **Accelerators** (TEST_DEVICE, ATLAS_800_A2/A3 series)

## Key Flags

| Flag | Description |
|------|-------------|
| `--num-queries` | Number of queries to simulate |
| `--query-length` | Input token length |
| `--context-length` | Context length for decode |
| `--decode` | Run decode-only simulation |
| `--quantize-linear-action` | Quantization: W8A8_DYNAMIC, W4A8, etc. |
| `--chrome-trace` | Generate Chrome trace file |
| `--device` | Device profile (TEST_DEVICE, ATLAS_800_A2\_\*, etc.) |
| `--tp-size`, `--dp-size`, `--ep-size` | Parallelism config |

## Output Interpretation

**Operator breakdown:**

```
tensor_cast.static_quant_linear.default      884.004ms       1.973ms         448
tensor_cast.attention.default                 259.855ms       4.060ms          64
aten.mul.Tensor                              198.215ms     237.668us         834
```

**Memory breakdown:**

```
Total device memory: 64.000 GB
  Model weight size: 31.981 GB
  KV cache: 1.719 GB
  Model activation size: 0.601 GB
  Memory available: 29.699 GB
```

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Model not found | HF model ID not accessible | Set `HF_ENDPOINT=https://hf-mirror.com` |
| Wrong memory estimate | Wrong device profile | Check `--device` matches hardware |
| Low TPS | Quantization disabled | Try `--quantize-linear-action W8A8_DYNAMIC` |
