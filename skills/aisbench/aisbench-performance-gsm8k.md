# AISBench Performance Evaluation Guide

Performance benchmarking measures throughput, latency, and concurrency of a running vLLM service. The CLI pattern is identical to accuracy evaluation — same model config, same datasets — with two differences:

1. Add `--mode perf`
2. Add `--summarizer default_perf`

______________________________________________________________________

## Prerequisite

A running vLLM server is required — see [SKILL.md](SKILL.md) Quick Start.

______________________________________________________________________

## Step 1 — Choose a Dataset

Performance eval supports all accuracy datasets plus `synthetic_gen` for custom sequence lengths.

**Option A: Use an existing dataset** (place files under `$LOCATION/ais_bench/datasets/` — see [aisbench-datasets.md](aisbench-datasets.md)):

```bash
ais_bench --models vllm_api_general_chat --datasets gsm8k_gen_0_shot_cot_chat_prompt --mode perf --search
```

**Option B: Synthetic dataset** (recommended for controlled input/output length testing):

```bash
ais_bench --models vllm_api_general_chat --datasets synthetic_gen --mode perf
```

Configure `synthetic_config.py` — see [aisbench-datasets.md](aisbench-datasets.md) for schema details.

______________________________________________________________________

## Step 2 — Run

**Text-only datasets:**

```bash
# C-Eval
ais_bench --models vllm_api_general_chat --datasets ceval_gen_0_shot_cot_chat_prompt.py --summarizer default_perf --mode perf

# MMLU
ais_bench --models vllm_api_general_chat --datasets mmlu_gen_0_shot_cot_chat_prompt.py --summarizer default_perf --mode perf

# GPQA
ais_bench --models vllm_api_general_chat --datasets gpqa_gen_0_shot_str.py --summarizer default_perf --mode perf

# MATH-500
ais_bench --models vllm_api_general_chat --datasets math500_gen_0_shot_cot_chat_prompt.py --summarizer default_perf --mode perf

# LiveCodeBench
ais_bench --models vllm_api_general_chat --datasets livecodebench_code_generate_lite_gen_0_shot_chat.py --summarizer default_perf --mode perf

# AIME 2024
ais_bench --models vllm_api_general_chat --datasets aime2024_gen_0_shot_chat_prompt.py --summarizer default_perf --mode perf

# GSM8K
ais_bench --models vllm_api_general_chat --datasets gsm8k_gen_0_shot_cot_chat_prompt.py --summarizer default_perf --mode perf
```

**Multi-modal (text + images) — uses streaming backend:**

```bash
# TextVQA
ais_bench --models vllm_api_stream_chat --datasets textvqa_gen_base64 --summarizer default_perf --mode perf
```

> **TextVQA dataset setup:** See [aisbench-datasets.md](aisbench-datasets.md) — download, reorganize, and fix image paths (absolute paths required to avoid a pydantic validation error).

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
