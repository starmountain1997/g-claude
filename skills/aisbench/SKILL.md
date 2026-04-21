---
name: aisbench
description: AISBench LLM evaluation framework. Use when installing AISBench, running accuracy benchmarks (GSM8K, MMLU, AIME, etc.), or running performance benchmarks (throughput, latency) against vLLM services on Ascend NPUs.
argument-hint: install / accuracy / performance
license: MIT
---

# AISBench Evaluation

AISBench evaluates LLM service accuracy and performance via an OpenAI-compatible API.

## Prerequisites

You need a running vLLM API server before benchmarking. If one isn't up yet:

- Use `/vllm` to install and launch the model as a service
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
- **Performance Benchmarking**: [aisbench-performance.md](aisbench-performance.md) — streaming backend, `ignore_eos`, synthetic dataset, concurrency sweep

## Run Commands via Shell Script

All `ais_bench` commands must be saved to a shell script and executed through it so output is captured in a timestamped log file. See the template in `/ascend` → "Common Requirement: Run via Shell Script with Log Output".

## Common Notes

- Results land in `outputs/default/<timestamp>/`
- Use `--debug` on first runs to see request logs on screen
- Use `--reuse <timestamp>` to resume interrupted runs or re-evaluate without re-running inference
- For accuracy: prefer `chat_prompt` dataset variants; use low temperature (`temperature=0`)
- For performance: `vllm_api_stream_chat` is required; `ignore_eos=True` is essential for meaningful throughput numbers
