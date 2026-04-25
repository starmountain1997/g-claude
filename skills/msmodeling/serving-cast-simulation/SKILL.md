---
name: serving-cast-simulation
description: ServingCast system-level simulation for LLM serving throughput and latency on Ascend NPUs. Use for multi-instance capacity planning, TTFT/TPOT optimization, and finding optimal vLLM parameters before deployment. Triggers when the user mentions serving throughput, multi-instance planning, capacity planning, or vLLM deployment optimization.
license: MIT
---

# ServingCast

System-level LLM serving simulation for multi-instance throughput and latency optimization.

## When to Use

- Multi-instance throughput under SLO constraints
- Prefill/Decode disaggregation planning
- Capacity planning (how many instances needed for target QPS)
- TTFT/TPOT optimization under latency limits
- Finding optimal vLLM parameters before real deployment

## What vs TensorCast

| This skill (ServingCast) | vs | [tensor-cast](../tensor-cast/) |
|--------------------------|----|-------------------------------|
| System-level, multi-instance | | Per-model, operator-level |
| Workload-driven simulation | | Model-driven analysis |
| How many instances needed? | | How fast is the model? |
| TTFT/TPOT under load | | FLOPs, memory footprint |

## Quick Start

1. **Write two configs** — `instances.yaml` (hardware/instances) + `common.yaml` (model/workload)
1. **Run simulation:**
   ```bash
   MSMODELING_PATH=$(uv pip show liuren_modeling 2>/dev/null | grep "Editable project location:" | cut -d':' -f2 | tr -d ' ')
   cd $MSMODELING_PATH
   python -m serving_cast.main \
     --instance_config_path=instances.yaml \
     --common_config_path=common.yaml
   ```
1. **Interpret results** — Check P90 TTFT/TPOT against targets
1. **Iterate** — Adjust `max_concurrency` and `max_tokens_budget` until targets met

## Config Files

See [msmodeling-usage.md](msmodeling-usage.md) for detailed schema.

### `instances.yaml` — Hardware & Parallelism

```yaml
instance_groups:
  - num_instances: 1
    num_devices_per_instance: 8  # 8 for 910B
    pd_role: both
    parallel_config:
      world_size: 8
      tp_size: 8
      dp_size: 1
      ep_size: 1
```

### `common.yaml` — Model & Workload

```yaml
model_config:
  name: Qwen/Qwen3-32B
  quantize_linear_action: W8A8_DYNAMIC

load_gen:
  num_requests: 500
  num_input_tokens: 512
  num_output_tokens: 256
  request_rate: 10.0

serving_config:
  max_concurrency: 64       # → vLLM --max-num-seqs
  max_tokens_budget: 8192   # → vLLM --max-num-batched-tokens
```

## Tuning Guide

| Symptom | Adjustment |
|---------|------------|
| P90 TTFT too high | Decrease `max_concurrency` |
| Throughput below target | Increase `max_concurrency` or `max_tokens_budget` |
| OOM | Decrease `max_tokens_budget` or increase `tp_size` |

**Rule:** `max_tokens_budget` should be ≥ `max_concurrency × avg_output_len`

## Supported Models

Always check the latest supported matrix:

```bash
MSMODELING_PATH=$(uv pip show liuren_modeling 2>/dev/null | grep "Editable project location:" | cut -d':' -f2 | tr -d ' ')
cat $MSMODELING_PATH/docs/en/tensor_cast_instruct.md | grep -A 20 "Supported Matrix"
```

## Output Interpretation

**Per-request latency:**

```
              E2E_TIME(s)  TTFT(s)  TPOT(s)
AVERAGE           1.23      0.45     0.012
P90               1.87      0.71     0.018
```

**Throughput:**

```
request_throughput(req/s)      10.37
output_token_throughput(tok/s) 2654.3
```

## CLI Reference

Show `throughput_optimizer` CLI arguments:

```bash
python /path/to/skills/msmodeling/serving-cast-simulation/scripts/show_throughput_optimizer_args.py
```

Or inline (requires msmodeling installed):

```bash
MSMODELING_PATH=$(uv pip show liuren_modeling 2>/dev/null | grep "Editable project location:" | cut -d':' -f2 | tr -d ' ')
python -c "
import sys
sys.path.insert(0, '$MSMODELING_PATH')
from cli.inference.throughput_optimizer import arg_parse
arg_parse().print_help()
"
```

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| `HF_MODEL_NOT_FOUND` | Model not on HuggingFace | Use supported model or `HF_ENDPOINT` |
| `num_devices_per_instance` mismatch | TP size ≠ 8 | Set to 8 for 910B |
| P90 TTFT too high | `max_concurrency` too high | Decrease `max_concurrency` |
| Throughput below target | Concurrency too low | Increase concurrency or `max_tokens_budget` |
| OOM during sim | `max_tokens_budget` too large | Decrease `max_tokens_budget` |
