---
name: aisbench
description: AISBench LLM evaluation framework. Use when running accuracy benchmarks (GSM8K, MMLU, AIME) or performance benchmarks (throughput, latency) against vLLM services on Ascend NPUs. Also use when installing or configuring AISBench, or when comparing model accuracy across different vLLM backends.
argument-hint: install / accuracy / performance / benchmark / gsm8k / mmlu / throughput
license: MIT
---

# AISBench Evaluation

AISBench evaluates LLM service accuracy and performance via an OpenAI-compatible API.

## Quick Start

Three steps from zero to results:

```bash
# 1. Verify NPU health
/ascend

# 2. Start vLLM service (keep terminal open)
/vllm-ascend

# 3. Run accuracy benchmark in a new terminal
ais_bench --models vllm_api_general_chat --datasets gsm8k_gen_4_shot_cot_chat_prompt --debug
```

Results land in `outputs/default/<timestamp>/`.

## Prerequisites

A **running vLLM API server** is required before any benchmark. If one isn't up yet:

- Use `/vllm-ascend` to install and launch the model as a service
- Use `/ascend` first to verify NPU health

Both accuracy and performance benchmarks share the same CLI structure:

```bash
ais_bench --models <model_task> --datasets <dataset_task> [--mode perf]
```

The only structural differences between accuracy and performance runs:

| | Accuracy | Performance |
|---|---|---|
| `--mode` flag | omit (default) | `--mode perf` |
| Model backend | text or streaming | **streaming only** (e.g. `vllm_api_stream_chat`) |
| `ignore_eos` | False | **True** (forces full output length) |
| Output dir | `summary/` (accuracy scores) | `performances/` (latency/throughput) |

## Start Here

Locate the AISBench installation before anything else:

```bash
pip show ais_bench_benchmark
```

If not found, follow [aisbench-install.md](aisbench-install.md). Use `Editable project location` as `$LOCATION`.

## Configure: Use `--search` to find config files

Every named task (model or dataset) corresponds to a `.py` config file. Find the paths:

```bash
ais_bench --models vllm_api_general_chat --datasets gsm8k_gen_4_shot_cot_chat_prompt --search
```

Edit the printed config files directly. Key model fields: `host_ip`, `host_port`, `model`, `max_out_len`, `batch_size`.

## Task Specifics

- **Installation**: [aisbench-install.md](aisbench-install.md)
- **Accuracy Evaluation**: [aisbench-accuracy.md](aisbench-accuracy.md) — dataset selection, model client config, troubleshooting
- **Performance Benchmarking**: [aisbench-performance-gsm8k.md](aisbench-performance-gsm8k.md) — streaming backend, `ignore_eos`, synthetic dataset, concurrency sweep

## Run via Shell Script

Always save `ais_bench` commands to a shell script — this captures output in a timestamped log for later inspection:

```bash
TS=$(date +%Y%m%d_%H%M%S)
LOG="run_${TS}.log"
echo "ais_bench [your flags]" > "$LOG"
ais_bench [your flags] 2>&1 | tee -a "$LOG"
```

Keep logs in `outputs/default/<timestamp>/` alongside results.

## Utilities

**Generate custom-length GSM8K datasets** for performance testing with controlled input/output sizes:

```bash
python scripts/make_gsm8k.py --input-len 64000 --batch-size 2800 --model-id deepseek-ai/DeepSeek-V3
```

Produces `GSM8K-in64000-bs2800.jsonl` for use with `--datasets` configs.

## Common Notes

- Results land in `outputs/default/<timestamp>/`
- Use `--debug` on first runs to see request logs on screen
- Use `--reuse <timestamp>` to re-evaluate accuracy results without re-running inference (e.g. after fixing answer extraction logic)
- For accuracy: prefer `chat_prompt` dataset variants; use low temperature (`temperature=0`)
- For performance: `vllm_api_stream_chat` is required; `ignore_eos=True` is essential for meaningful throughput numbers
