# AISBench Performance Evaluation Guide

Performance benchmarking measures throughput, latency, and concurrency of a running vLLM service. The CLI pattern is identical to accuracy evaluation — same model config, same datasets — with two differences:

1. Add `--mode perf`
1. Add `--summarizer default_perf`

______________________________________________________________________

## Prerequisite

A running vLLM server is required — see [SKILL.md](SKILL.md) Quick Start.

______________________________________________________________________

## Step 1 — Choose a Dataset

Use the **Synthetic dataset** — no download needed, fully controlled input/output lengths:

```bash
ais_bench --models vllm_api_general_chat --datasets synthetic_gen --mode perf
```

Configure `$LOCATION/ais_bench/datasets/synthetic/synthetic_config.py`:

```python
synthetic_config = {
    "Type": "string",
    "RequestCount": 1000,
    "StringConfig": {
        "Input":  {"Method": "uniform", "Params": {"MinValue": 512, "MaxValue": 2048}},
        "Output": {"Method": "uniform", "Params": {"MinValue": 128, "MaxValue": 512}},
    }
}
```

> **Before running, ask the user:** "What input and output length ranges do you want for the synthetic dataset?" Defaults above are 512–2048 input, 128–512 output.

______________________________________________________________________

## Step 2 — Run

```bash
ais_bench --models vllm_api_general_chat --datasets synthetic_gen --summarizer default_perf --mode perf
```

______________________________________________________________________

## Step 3 — Read Results

Results are printed at the end and saved under `outputs/default/<timestamp>/performances/<model-abbr>/`:

- `<dataset>.csv` — per-request latency breakdown
- `<dataset>.json` — end-to-end summary metrics
- `<dataset>_plot.html` — concurrency visualization (open in browser)

Key metrics:

| Metric | What it measures |
|--------|-----------------|
| **TTFT** | Time To First Token — prefill latency |
| **TPOT** | Time Per Output Token — per-step decode latency |
| **E2EL** | End-to-End Latency — total wall-clock per request |
| **Output Token Throughput** | decode tokens/s — primary throughput metric |
| **Total Token Throughput** | (input + output) tokens/s |

______________________________________________________________________

## Concurrency Sweep

To find the throughput saturation point, sweep `batch_size`:

```bash
CONFIG=$LOCATION/ais_bench/benchmark/configs/models/vllm_api/vllm_api_general_chat.py
for BS in 1 4 16 64 128 256; do
    sed -i "s/batch_size=.*/batch_size=$BS,/" $CONFIG
    ais_bench --models vllm_api_general_chat --datasets synthetic_gen --mode perf --num-prompts 200
done
```

______________________________________________________________________

## Troubleshooting

**All requests fail**: service unreachable or OOM. Halve `batch_size` and retry. Check `curl http://<host>:<port>/v1/models`.

**Recalculate metrics without re-running** (e.g., to add P95 percentile):

Edit the summarizer config, then:

```bash
ais_bench --models vllm_api_general_chat --datasets gsm8k_gen_0_shot_cot_chat_prompt \
          --summarizer default_perf --mode perf_viz --pressure --reuse 20250628_151326
```
