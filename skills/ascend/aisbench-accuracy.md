# AISBench Accuracy Evaluation Guide

AISBench evaluates LLM service accuracy via an OpenAI-compatible API.

______________________________________________________________________

## Locate the Installation

AISBench is installed in editable mode. Find its source root before doing anything else:

```bash
pip show ais_bench_benchmark
```

If the package is not found, follow [aisbench-install.md](aisbench-install.md) to install it first, then return here.

Use the `Editable project location` field from `pip show` as the root for all config paths below.

______________________________________________________________________

## Setup: Two Things to Configure

Every evaluation needs exactly two pieces of configuration:

1. **Dataset** — which benchmark to run, and which config variant to use
2. **Model client** — how to reach the vLLM service

Work through them in order.

______________________________________________________________________

## Step 1 — Dataset

Ask the user: **which dataset do you want to use?**

Once they answer, investigate the AISBench installation to check support and requirements:

Use `$LOCATION` to mean the `Editable project location` path from `pip show ais_bench_benchmark`.

1. **Check if the dataset is supported** — look for a matching folder:
   ```bash
   ls $LOCATION/ais_bench/benchmark/configs/datasets/
   ```

2. **Read the dataset README** to understand:
   - What the dataset tests
   - Whether it requires a VLM (multimodal) or works with text-only LLMs
   - How to obtain the data files and where to place them
   ```bash
   cat $LOCATION/ais_bench/benchmark/configs/datasets/<dataset>/README.md
   ```

3. **List available config variants** for that dataset:
   ```bash
   ls $LOCATION/ais_bench/benchmark/configs/datasets/<dataset>/
   ```
   For accuracy eval, prefer `chat_prompt` variants (e.g. `gsm8k_gen_0_shot_cot_chat_prompt`).

4. **Check model compatibility**: if the dataset is multimodal (images/video/audio), the user's model must be a VLM with vision support enabled in vLLM. If the user's model is a text-only LLM, tell them and suggest a text-only alternative.

Report your findings to the user — dataset name confirmed, variant chosen, data placement instructions — before moving to Step 2.

______________________________________________________________________

## Step 2 — Model Client

Ask the user:
- **vLLM host IP** — e.g. `localhost` or a remote IP
- **vLLM port** — e.g. `8080`
- **Model-served-name** — from `curl http://<host>:<port>/v1/models`

### Create the config file

Copy the example template from the AISBench source (`$LOCATION` = `Editable project location` from `pip show ais_bench_benchmark`) to the current working directory:

```bash
cp $LOCATION/ais_bench/configs/api_examples/infer_vllm_api_stream_chat.py ./eval.py
```

Edit `eval.py`. There are two things to set:

**1. Dataset import** — replace the gsm8k import with the dataset chosen in Step 1:

```python
with read_base():
    from ais_bench.benchmark.configs.datasets.<dataset>.<variant> import <dataset>_datasets as datasets_to_eval

datasets = [
    *datasets_to_eval,
]
```

**2. Model fields**:

```python
from ais_bench.benchmark.models import VLLMCustomAPIChat
from ais_bench.benchmark.utils.postprocess.model_postprocessors import extract_non_reasoning_content

models = [
    dict(
        attr="service",
        type=VLLMCustomAPIChat,
        abbr="vllm-api-stream-chat",
        path="/path/to/model",     # ← local path of the model
        model="",                  # ← vLLM served model name (from /v1/models); empty = auto-detect
        stream=True,
        request_rate=0,
        use_timestamp=False,
        retry=2,
        api_key="",
        host_ip="localhost",       # ← vLLM host IP
        host_port=8080,            # ← vLLM port
        url="",
        max_out_len=512,           # ← set according to vLLM --max-model-len config
        batch_size=1,              # ← set according to vLLM --max-num-seqs / available memory
        trust_remote_code=False,
        generation_kwargs=dict(
            temperature=0.01,      # ← use low temperature for deterministic accuracy eval
            ignore_eos=False,
        ),
        pred_postprocessor=dict(type=extract_non_reasoning_content),
    )
]
```

______________________________________________________________________

## Step 3 — Run

```bash
ais_bench eval.py
```

Results in `outputs/default/<timestamp>/summary/summary_*.txt`.

______________________________________________________________________

## Troubleshooting: Accuracy Too Low

### Step 1 — Inspect raw model outputs

Predictions are saved as JSONL (one JSON object per line) under:

```
outputs/default/<timestamp>/predictions/<model-abbr>/<dataset>.jsonl
```

Each line has this structure:

```json
{
  "data_abbr": "gsm8k",
  "id": 0,
  "success": true,
  "uuid": "...",
  "origin_prompt": "...",
  "prediction": "<model output>",
  "gold": "<expected answer>"
}
```

Print a few samples to see what the model is actually producing:

```bash
head -n 5 outputs/default/<timestamp>/predictions/<model-abbr>/<dataset>.jsonl | python3 -c "
import sys, json
for line in sys.stdin:
    d = json.loads(line)
    print('--- id', d['id'])
    print('GOLD     :', d.get('gold'))
    print('PREDICT  :', d.get('prediction'))
    print()
"
```

If some requests failed, check the failed file:

```bash
cat outputs/default/<timestamp>/predictions/<model-abbr>/<dataset>_failed.jsonl
```

### Step 2 — Diagnose from what you see

#### Output truncated (answers cut off mid-sentence)

The model is hitting a length limit before finishing. Check two things:

1. **vLLM `--max-model-len`** — if set too low on the server side, responses are cut. Check the vLLM launch command (see `vllm-run.md`).
2. **`max_out_len` in `eval.py`** — raise it (e.g. `1024` → `2048`) and rerun.

#### Output is garbled

The model is generating incoherent tokens. This is a model-level issue — likely a quantization accuracy regression. Tell the user: the quantization config needs further tuning (e.g. adjust quantization sensitivity or exclude affected layers — see `msmodelslim.md`).

#### Prediction format wrong (correct answer present but not extracted)

The model produces the right answer but the evaluator misses it — e.g. the number appears inside a sentence rather than at the end. Check whether `pred_postprocessor` is set correctly in `eval.py`. For reasoning models (DeepSeek-R1, QwQ), ensure `extract_non_reasoning_content` is applied so the `<think>...</think>` block is stripped before evaluation.

#### Failures (`success: false` in the JSONL)

Network or server errors during inference. Check `error_info` in `<dataset>_failed.jsonl`. Common causes: vLLM OOM (reduce `batch_size`), request timeout (check vLLM logs), or model not loaded yet.

