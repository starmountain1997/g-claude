---
name: msmodeling
description: MindStudio-Modeling performance evaluation and deployment strategy tuning on Ascend NPUs. Use this skill whenever you need to simulate LLM serving throughput/latency, find optimal vLLM parameters (--max-num-seqs, --max-num-batched-tokens, --tensor-parallel-size), or before running real vLLM experiments on Ascend hardware. Trigger when the user mentions performance tuning, deployment optimization, NPU benchmarking, or wants to validate vLLM config values.
license: MIT
---

# MindStudio-Modeling

MindStudio-Modeling (msmodeling) simulates theoretical LLM serving performance on Ascend NPUs and finds optimal deployment parameters before any real hardware run.

**When to use this skill:** Before Phase 2 (real vLLM runs) in the ascend pipeline, or whenever you need to tune vLLM parameters for Ascend NPUs.

**Entry point**: `python -m serving_cast.main --instance_config_path=<hw.yaml> --common_config_path=<workload.yaml>`

## When NOT to Use

- If you have real benchmark data already — use it directly instead of simulating
- If the model isn't in the supported matrix (check via `pip show msmodeling` and read the source doc)

## Pipeline Context

This skill bridges Phase 0 (workload characterization) and Phase 2 (real vLLM runs):

```
[vllm-ascend Phase 0] → collect workload dimensions (input/output tokens, QPS)
        ↓
[msmodeling] → simulate to find optimal --max-num-seqs, --max-num-batched-tokens
        ↓
[vllm-ascend Phase 2] → apply validated params to real hardware
```

## Quick Start

1. **Gather inputs** — Get hardware info (`npu-smi info`) and workload dims from Phase 0
2. **Write two configs** — `instances.yaml` (hardware) + `common.yaml` (model/workload)
3. **Run simulation** — `python -m serving_cast.main --instance_config_path=... --common_config_path=...`
4. **Interpret results** — Check P90 TTFT/TPOT against targets
5. **Iterate** — Adjust `max_concurrency` and `max_tokens_budget` until targets met

## Installation

See [msmodeling-install.md](msmodeling-install.md) for:
- Cloning the repo
- Installing dependencies
- Setting `PYTHONPATH` and `HF_ENDPOINT`

## Usage & vLLM Integration

See [msmodeling-usage.md](msmodeling-usage.md) for:
- Config file schemas (`instances.yaml`, `common.yaml`)
- Step-by-step simulation workflow
- Output interpretation
- Mapping results to vLLM parameters

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| `HF_MODEL_NOT_FOUND` | Model ID not on HuggingFace | Use supported model or set `HF_ENDPOINT=https://hf-mirror.com` |
| `num_devices_per_instance` mismatch | TP size doesn't match hardware | Set `num_devices_per_instance: 8` for 910B |
| P90 TTFT too high | `max_concurrency` too high | Decrease `max_concurrency` (→ lower `--max-num-seqs`) |
| Throughput below target | Concurrency too low | Increase `max_concurrency` or `max_tokens_budget` |
| OOM during simulation | `max_tokens_budget` too large | Decrease `max_tokens_budget` |

## Supported Models & Devices

**Always check the latest supported matrix in the source doc:**

```bash
MSMODELING_PATH=$(pip show msmodeling | grep "Location:" | cut -d' ' -f2)
cat $MSMODELING_PATH/source_code_path/docs/en/tensor_cast_instruct.md | grep -A 20 "Supported Matrix"
```

This lists supported:
- **Text model families** (Qwen3, GLM-4, DeepSeek V3, etc.)
- **Vision-language models** (Qwen3-VL, InternVL, etc.)
- **Video generation models** (Wan, HunyuanVideo)
- **Quantization types** (W8A16/W8A8/W4A8, FP8, MXFP4)
- **Accelerators** (TEST_DEVICE, ATLAS_800_A2/A3 series)

## Tips

- Start with `max_concurrency: 64` and adjust based on TTFT targets
- `max_tokens_budget` should be ≥ `max_concurrency × avg_output_len`
- Use `world_size: 8` and `tp_size: 8` for single-node 910B
- Set `request_rate` to your target QPS from Phase 0
