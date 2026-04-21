---
name: aisbench
description: AISBench LLM evaluation framework. Use when installing AISBench, running accuracy benchmarks (GSM8K, MMLU, etc.), or running performance benchmarks (throughput, latency) against vLLM services on Ascend NPUs.
argument-hint: install / accuracy / performance
---

# AISBench Evaluation

AISBench evaluates LLM service accuracy and performance via an OpenAI-compatible API.

## Start Here

Before any evaluation task, locate the AISBench installation:

```bash
pip show ais_bench_benchmark
```

If not found, follow [aisbench-install.md](aisbench-install.md) to install first.

Use the `Editable project location` field as `$LOCATION` in all paths.

## Task Specifics

- **Installation**: See [aisbench-install.md](aisbench-install.md)
- **Accuracy Evaluation**: See [aisbench-accuracy.md](aisbench-accuracy.md) — dataset selection, model client config, and accuracy troubleshooting
- **Performance Benchmarking**: See [aisbench-performance.md](aisbench-performance.md) — throughput/latency measurement with GSM8K dataset generation

## Common Notes

- AISBench is installed in editable mode — always use `pip show` to find the source path
- For accuracy evals, prefer `chat_prompt` dataset variants
- For performance evals, use `ignore_eos=True` and `request_rate=0` (burst mode) to measure peak throughput
- Results land in `outputs/default/<timestamp>/`
