---
name: aisbench
description: AISBench LLM evaluation framework. Use when running accuracy benchmarks (GSM8K, MMLU, GPQA, MATH-500, LiveCodeBench, AIME, C-Eval) or performance benchmarks (throughput, latency, multi-modal) against vLLM services on Ascend NPUs. Also use when installing or configuring AISBench, or when comparing model accuracy across different vLLM backends.
argument-hint: install / accuracy / performance / benchmark / gsm8k / mmlu / gpqa / aime / ceval / throughput
license: MIT
---

# AISBench Evaluation

AISBench evaluates LLM service accuracy and performance via an OpenAI-compatible API.

## Quick Start

A **running vLLM API server** is required before any benchmark. If one isn't up yet:

```bash
/ascend        # 1. Verify NPU health
/vllm-ascend   # 2. Start vLLM service (keep terminal open)
```

Then run the benchmark in a new terminal:

```bash
ais_bench --models vllm_api_general_chat --datasets gsm8k_gen_4_shot_cot_chat_prompt --debug
```

Results land in `outputs/default/<timestamp>/`.

Accuracy and performance benchmarks share the same CLI structure:

```bash
ais_bench --models <model_task> --datasets <dataset_task> [--mode perf]
```

The only structural differences between accuracy and performance runs:

| | Accuracy | Performance |
|---|---|---|
| `--mode` flag | omit (default) | `--mode perf` |
| `--summarizer` | omit | `--summarizer default_perf` |
| Output dir | `summary/` (accuracy scores) | `performances/` (latency/throughput) |

## Start Here

Locate the AISBench installation before anything else:

```bash
pip show ais_bench_benchmark
```

If not found, follow [aisbench-install.md](aisbench-install.md). Use `Editable project location` as `$LOCATION`.

## Configure Model Client

Both accuracy and performance evaluations edit the same config file. Find its path:

```bash
ais_bench --models vllm_api_general_chat --datasets gsm8k_gen_0_shot_cot_chat_prompt --search
```

Edit `benchmark/ais_bench/benchmark/configs/models/vllm_api/vllm_api_general_chat.py`:

Key fields:
- `attr`: inference backend type — `service` (vLLM serving) or `local` (local model)
- `type`: backend API class
- `abbr`: unique task identifier (used to distinguish multiple concurrent tasks)
- `path`: model weight path
- `model`: model name as registered in vLLM (`/v1/models`)
- `host_ip` / `host_port`: vLLM server address
- `max_out_len`: `max_out_len` + input length must not exceed vLLM's `max_model_len`; `32768` works for most datasets
- `batch_size`: concurrent requests — adjust per dataset
- `temperature`: generation parameter

```python
from ais_bench.benchmark.models import VLLMCustomAPIChat
from ais_bench.benchmark.utils.model_postprocessors import extract_non_reasoning_content

models = [
    dict(
        attr="service",
        type=VLLMCustomAPIChat,
        abbr='vllm-api-general-chat',
        path="xxxx",
        model="xxxx",
        request_rate=0,
        retry=2,
        host_ip="localhost",
        host_port=8000,
        max_out_len=32768,
        batch_size=4,
        trust_remote_code=False,
        generation_kwargs=dict(
            temperature=0.6,
            top_k=10,
            top_p=0.95,
            seed=None,
            repetition_penalty=1.03,
        ),
        pred_postprocessor=dict(type=extract_non_reasoning_content)
    )
]
```

> Multi-modal performance benchmarks (TextVQA) use a separate streaming backend — see [aisbench-performance.md](aisbench-performance.md).

The dataset config rarely needs changes if data is placed correctly under `ais_bench/datasets/`.

## Task Specifics

- **Installation**: [aisbench-install.md](aisbench-install.md)
- **Dataset Download**: [aisbench-datasets.md](aisbench-datasets.md) — download commands for all datasets (C-Eval, MMLU, GPQA, MATH-500, LiveCodeBench, AIME, GSM8K, TextVQA, synthetic)
- **Accuracy Evaluation**: [aisbench-accuracy.md](aisbench-accuracy.md) — run commands for all datasets, output structure, troubleshooting
- **Performance Benchmarking**: [aisbench-performance.md](aisbench-performance.md) — synthetic dataset, concurrency sweep, multi-modal

## Run via Shell Script

Always save `ais_bench` commands to a shell script — this captures output in a timestamped log for later inspection:

```bash
TS=$(date +%Y%m%d_%H%M%S)
LOG="run_${TS}.log"
echo "ais_bench [your flags]" > "$LOG"
ais_bench [your flags] 2>&1 | tee -a "$LOG"
```

Keep logs in `outputs/default/<timestamp>/` alongside results.

## Before Running: Ask the User

Before issuing any `ais_bench` command, ask:

> "Do you want to run on the full dataset, or limit to a smaller number of prompts first (e.g. 100) to validate the setup?"

Full datasets can take a long time. A limited run is cheap and catches config errors early. Add `--num-prompts <N>` to cap the sample count — it works for both accuracy and performance modes.

## Common Notes

- Use `--debug` on first runs to see request logs on screen
- For accuracy: prefer `chat_prompt` dataset variants; use low temperature (`temperature=0`)
- For performance: `vllm_api_stream_chat` is required; `ignore_eos=True` is essential for meaningful throughput numbers
