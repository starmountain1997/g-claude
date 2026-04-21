# AISBench Performance Evaluation Guide

This guide covers performance benchmarking (throughput, latency, concurrency) for LLM services on Ascend NPUs using AISBench.

______________________________________________________________________

## Locate the Installation

AISBench is installed in editable mode. Find its source root before doing anything else:

```bash
pip show ais_bench_benchmark
```

If the package is not found, follow [aisbench-install.md](aisbench-install.md) to install it first, then return here.

Use the `Editable project location` field from `pip show` as `$LOCATION` in all paths below.

______________________________________________________________________

## Step 1 — Prepare the Dataset

For performance benchmarking you need a dataset with a fixed, controlled input length and a known batch size. Use the provided script to generate one from GSM8K.

**Requirements**: `pip install click loguru modelscope transformers`

```bash
python ${CLAUDE_SKILL_DIR}/scripts/make_gsm8k.py \
    --input-len 64000 \
    --batch-size 2800 \
    --model-id deepseek-ai/DeepSeek-V3 \
    --zip-path ./gsm8k.zip
```

This produces `GSM8K-in{input_len}-bs{batch_size}.jsonl` (e.g. `GSM8K-in64000-bs2800.jsonl`) in the current directory. Each line is `{"question": "<text padded/truncated to input_len tokens>", "answer": "none"}`.

**Options**:

- `--input-len`: Target token count per sample (text is repeated then truncated to hit this length exactly).
- `--batch-size`: Total number of samples in the output file.
- `--model-id`: Tokenizer to use for token counting (downloaded via ModelScope).
- `--zip-path`: Path to GSM8K zip (auto-downloaded from OpenCompass if absent).

______________________________________________________________________

## Step 2 — Configure the Model Client

Ask the user:

- **vLLM host IP** — e.g. `localhost` or a remote IP
- **vLLM port** — e.g. `8080`
- **Model-served-name** — from `curl http://<host>:<port>/v1/models`
- **Target concurrency** — how many concurrent requests to send
- **Output length** — max tokens to generate per request

### Locate the config file

```bash
ais_bench --models vllm_api_stream_chat --mode perf --search
```

Copy it to the working directory:

```bash
cp $LOCATION/ais_bench/benchmark/configs/models/vllm_api/vllm_api_stream_chat.py ./perf_model.py
```

Edit `perf_model.py`:

```python
from ais_bench.benchmark.models import VLLMCustomAPIChatStream

models = [
    dict(
        attr="service",
        type=VLLMCustomAPIChatStream,
        abbr='vllm-api-stream-chat',
        path="",
        model="DeepSeek-V3",   # ← vLLM served model name (from /v1/models); empty = auto-detect
        request_rate=0,        # ← 0 = burst (all requests at once); use float for rate-limited
        retry=2,
        host_ip="localhost",   # ← vLLM host IP
        host_port=8080,        # ← vLLM port
        max_out_len=2048,      # ← desired output length for this test case
        batch_size=200,        # ← concurrent requests (tune to target concurrency)
        generation_kwargs=dict(
            temperature=1.0,
            top_p=1.0,
            seed=None,
            ignore_eos=True,   # ← force output to reach max_out_len (no early stop)
        )
    )
]
```

Key fields for performance testing:

- `batch_size`: concurrency level — the primary variable to sweep across runs
- `max_out_len`: must match the desired output length for the test
- `ignore_eos=True`: prevents early EOS so every request generates exactly `max_out_len` tokens
- `request_rate=0`: burst mode — all requests sent immediately for max-throughput measurement

______________________________________________________________________

## Step 3 — Run

```bash
ais_bench \
    --models ./perf_model.py \
    --custom-dataset-path ./GSM8K-in64000-bs2800.jsonl \
    --custom-dataset-data-type qa \
    --mode perf \
    --debug
```

Add `--num-prompts N` to cap the number of requests (useful for smoke tests or warm-up):

```bash
ais_bench \
    --models ./perf_model.py \
    --custom-dataset-path ./GSM8K-in64000-bs2800.jsonl \
    --mode perf \
    --num-prompts 100
```

Results are saved under `outputs/default/<timestamp>/` and printed to screen.

______________________________________________________________________

## Step 4 — Read the Results

Performance results are printed at the end of the run:

```
Performance Parameters  | Average       | P75           | P90           | P99
E2EL                    | 2048 ms       | ...           | ...           | ...
TTFT                    | 50 ms         | ...           | ...           | ...
TPOT                    | 10 ms         | ...           | ...           | ...
OutputTokenThroughput   | 3200 token/s  | ...           | ...           | ...

Common Metric                | Value
Output Token Throughput      | 3200 token/s
Total Token Throughput       | 4000 token/s
Request Throughput           | 1.5 req/s
Concurrency                  | 128
```

Key metrics:

- **TTFT** (Time To First Token): prefill latency — reflects KV cache fill cost
- **TPOT** (Time Per Output Token): per-step decode latency
- **E2EL** (End-to-End Latency): total wall-clock time per request
- **Output Token Throughput**: decode tokens/s — the primary throughput metric
- **Total Token Throughput**: (input + output) tokens/s

Detailed per-request CSV/JSON and a concurrency visualization HTML are saved at:
`outputs/default/<timestamp>/performances/vllm-api-stream-chat/`

______________________________________________________________________

## Troubleshooting

### Output token count is lower than `max_out_len`

The model stopped early despite `ignore_eos=True`. Some backends don't support `ignore_eos`. Check whether the vLLM version passes the parameter through; if not, use `min_tokens` in `generation_kwargs` to set a minimum output floor.

### All requests fail (`Failed Requests = N`)

vLLM is unreachable or OOMing. Check:

1. Is the service running? `curl http://<host>:<port>/v1/models`
1. Is `batch_size` too high for available HBM? Halve it and retry.
1. Check vLLM logs for OOM or NCCL errors.

### Throughput lower than expected

1. Confirm `ignore_eos=True` is effective — low `OutputTokens` average in results means requests are stopping early.
1. Check `request_rate` — if set above 0.1, requests are rate-limited, reducing observed throughput.
1. Run a concurrency sweep to find the saturation point:

```bash
for BS in 1 4 16 64 128 256; do
    sed -i "s/batch_size=.*/batch_size=$BS,/" ./perf_model.py
    ais_bench \
        --models ./perf_model.py \
        --custom-dataset-path ./GSM8K-in64000-bs2800.jsonl \
        --mode perf
done
```
