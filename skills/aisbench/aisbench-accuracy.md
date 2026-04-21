# AISBench Accuracy Evaluation Guide

AISBench evaluates model accuracy by sending requests to a running vLLM service and comparing outputs against reference answers.

______________________________________________________________________

## Prerequisite: vLLM Service

Both accuracy and performance benchmarks require an OpenAI-compatible vLLM server. Start it like:

```bash
vllm serve /path/to/model --host 0.0.0.0 --port 8080 --served-model-name DeepSeek-R1
```

Verify it's up: `curl http://<host>:<port>/v1/models`

______________________________________________________________________

## Step 1 — Locate AISBench

```bash
pip show ais_bench_benchmark
```

If not found, follow [aisbench-install.md](aisbench-install.md). Use `Editable project location` as `$LOCATION`.

______________________________________________________________________

## Step 2 — Choose a Dataset

Ask the user which benchmark to run. List available datasets:

```bash
ls $LOCATION/ais_bench/benchmark/configs/datasets/
```

Read the dataset README to understand data file requirements and placement:

```bash
cat $LOCATION/ais_bench/benchmark/configs/datasets/$DATASET/README.md
```

List config variants for the dataset:

```bash
ls $LOCATION/ais_bench/benchmark/configs/datasets/$DATASET/
```

Prefer `chat_prompt` variants for accuracy eval (e.g. `gsm8k_gen_4_shot_cot_chat_prompt`). Place dataset files under `$LOCATION/ais_bench/datasets/`.

______________________________________________________________________

## Step 3 — Configure Model and Dataset

Find the config file paths with `--search`:

```bash
ais_bench --models vllm_api_general_chat --datasets gsm8k_gen_4_shot_cot_chat_prompt --search
```

This prints absolute paths to the model and dataset config `.py` files. Edit the **model config** (`vllm_api_general_chat.py`):

```python
from ais_bench.benchmark.models import VLLMCustomAPIChat

models = [
    dict(
        attr="service",
        type=VLLMCustomAPIChat,
        abbr='vllm-api-general-chat',
        path="",                   # tokenizer path (optional for accuracy eval)
        model="DeepSeek-R1",       # model name from /v1/models; empty = auto-detect
        request_rate=0,            # <0.1 = send all at once
        retry=2,
        host_ip="localhost",       # ← vLLM host IP
        host_port=8080,            # ← vLLM port
        max_out_len=512,           # ← raise if answers are truncated
        batch_size=4,              # ← concurrent requests
        generation_kwargs=dict(
            temperature=0,         # low temperature for deterministic accuracy
            top_p=0.95,
            seed=None,
        )
    )
]
```

The dataset config rarely needs changes if data is in `ais_bench/datasets/`.

______________________________________________________________________

## Step 4 — Run

```bash
ais_bench --models vllm_api_general_chat --datasets gsm8k_gen_4_shot_cot_chat_prompt --debug
```

`--debug` prints request logs to screen (recommended on first run). Drop it for batch runs.

Results are printed at the end and saved under `outputs/default/<timestamp>/`:

- `summary/summary_*.txt|csv|md` — final accuracy scores
- `predictions/<model>/` — raw model outputs (JSON) for inspection
- `results/<model>/` — per-sample evaluation scores
- `logs/` — infer and eval phase logs

______________________________________________________________________

## Multi-Task Evaluation

Run multiple models or datasets in one command:

```bash
ais_bench --models vllm_api_general_chat vllm_api_stream_chat \
          --datasets gsm8k_gen_4_shot_cot_str aime2024_gen_0_shot_chat_prompt
```

Tasks = product of models × datasets. For parallel execution (lower concurrency per task):

```bash
ais_bench --models vllm_api_general_chat --datasets gsm8k_gen aime2024_gen \
          --disable-cb --max-num-workers 4
```

______________________________________________________________________

## Resume an Interrupted Run

```bash
ais_bench --models vllm_api_general_chat --datasets gsm8k_gen --reuse 20250628_151326
```

______________________________________________________________________

## Troubleshooting

**Accuracy too low — inspect raw outputs:**

```bash
cat outputs/default/$TS/predictions/vllm-api-general-chat/gsm8k.json | \
  python3 -c "import sys,json; [print(json.loads(l)['prediction'][:200]) for l in sys.stdin]" | head -20
```

- **Truncated output**: raise `max_out_len`; check vLLM `--max-model-len`
- **Wrong answer format extracted**: add `pred_postprocessor=dict(type=extract_non_reasoning_content)` to model config (strips `<think>...</think>` for reasoning models)
- **Failed requests**: check `predictions/.../gsm8k_failed.json`; reduce `batch_size` if OOM

**Re-evaluate without re-running inference** (e.g., to fix answer extraction):

```bash
ais_bench --models vllm_api_general_chat --datasets gsm8k_gen --mode eval --reuse 20250628_151326
```
