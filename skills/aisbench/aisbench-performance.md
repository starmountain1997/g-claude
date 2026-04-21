# AISBench Performance Evaluation Guide

Performance benchmarking measures throughput, latency, and concurrency of a running vLLM service. The CLI pattern is identical to accuracy evaluation with two differences:

1. Add `--mode perf`
1. Use a **streaming** model backend (`vllm_api_stream_chat` instead of `vllm_api_general_chat`)

______________________________________________________________________

## Prerequisite: vLLM Service

```bash
vllm serve /path/to/model --host 0.0.0.0 --port 8080 --served-model-name DeepSeek-R1
```

______________________________________________________________________

## Step 1 — Locate AISBench

```bash
pip show ais_bench_benchmark
```

Use `Editable project location` as `$LOCATION`.

______________________________________________________________________

## Step 2 — Choose a Dataset

Performance eval supports all accuracy datasets plus `synthetic_gen` for custom sequence lengths.

**Option A: Use an existing dataset** (same as accuracy eval — place files under `$LOCATION/ais_bench/datasets/`):

```bash
ais_bench --models vllm_api_stream_chat --datasets demo_gsm8k_gen_4_shot_cot_chat_prompt --mode perf --search
```

**Option B: Synthetic dataset** (recommended for controlled input/output length testing):

```bash
ais_bench --models vllm_api_stream_chat --datasets synthetic_gen --mode perf
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

______________________________________________________________________

## Step 3 — Configure the Model Client

Find the config file path:

```bash
ais_bench --models vllm_api_stream_chat --mode perf --search
```

Edit `vllm_api_stream_chat.py`:

```python
from ais_bench.benchmark.models import VLLMCustomAPIChatStream

models = [
    dict(
        attr="service",
        type=VLLMCustomAPIChatStream,
        abbr='vllm-api-stream-chat',
        path="",
        model="DeepSeek-R1",       # model name from /v1/models; empty = auto-detect
        request_rate=0,            # 0 = burst mode (all requests at once); use float for rate-limited
        retry=2,
        host_ip="localhost",       # ← vLLM host IP
        host_port=8080,            # ← vLLM port
        max_out_len=512,           # ← output length for this test case
        batch_size=64,             # ← concurrency (primary variable to sweep)
        generation_kwargs=dict(
            temperature=1.0,
            top_p=1.0,
            seed=None,
            ignore_eos=True,       # ← force output to reach max_out_len (no early stop)
        )
    )
]
```

Key differences from accuracy config:

- `type=VLLMCustomAPIChatStream` (streaming required)
- `ignore_eos=True` (forces full output length — essential for meaningful throughput numbers)
- Higher `batch_size` (concurrency is the main variable to sweep)

______________________________________________________________________

## Step 4 — Run

```bash
ais_bench --models vllm_api_stream_chat --datasets demo_gsm8k_gen_4_shot_cot_chat_prompt --mode perf --debug
```

Cap request count for smoke tests:

```bash
ais_bench --models vllm_api_stream_chat --datasets demo_gsm8k_gen_4_shot_cot_chat_prompt --mode perf --num-prompts 100
```

______________________________________________________________________

## Step 5 — Read Results

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
for BS in 1 4 16 64 128 256; do
    sed -i "s/batch_size=.*/batch_size=$BS,/" $LOCATION/ais_bench/benchmark/configs/models/vllm_api/vllm_api_stream_chat.py
    ais_bench --models vllm_api_stream_chat --datasets synthetic_gen --mode perf --num-prompts 200
done
```

______________________________________________________________________

## Troubleshooting

**Output tokens lower than `max_out_len`**: `ignore_eos` not taking effect. Add `min_tokens` to `generation_kwargs` as a fallback minimum.

**All requests fail**: service unreachable or OOM. Halve `batch_size` and retry. Check `curl http://<host>:<port>/v1/models`.

**Recalculate metrics without re-running** (e.g., to add P95 percentile):

Edit the summarizer config, then:

```bash
ais_bench --models vllm_api_stream_chat --datasets demo_gsm8k_gen_4_shot_cot_chat_prompt \
          --summarizer default_perf --mode perf_viz --pressure --reuse 20250628_151326
```
