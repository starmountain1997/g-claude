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
models = [
    dict(
        ...
        model="",             # ← model-served-name; empty string = auto-detect
        host_ip="localhost",  # ← vLLM host IP
        host_port=8080,       # ← vLLM port
        max_out_len=512,      # ← 1024 for text models; 256 for VLM (answers are short)
        batch_size=1,         # ← 32 for text models; 8–16 for VLM (vision encoding is memory-intensive)
        generation_kwargs=dict(
            temperature=0.0,  # ← use 0.0 for deterministic accuracy eval
            top_k=1,
            top_p=1.0,
            seed=42,
            repetition_penalty=1.0,
        )
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

First, inspect the raw model outputs to understand what went wrong:

```bash
cat outputs/default/<timestamp>/predictions/<model-abbr>/<dataset>.json
```

### Output truncated (answers cut off mid-sentence)

The model is hitting a length limit before finishing. Check two things:

1. **vLLM `--max-model-len`** — if set too low on the server side, responses are cut. Check the vLLM launch command (see `vllm-run.md`).
2. **`max_out_len` in `eval.py`** — raise it (e.g. `1024` → `2048`) and rerun.

### Output is garbled 

The model is generating incoherent tokens. This is a model-level issue — likely a quantization accuracy regression. Tell the user: the quantization config needs further tuning (e.g. adjust quantization sensitivity or exclude affected layers — see `msmodelslim.md`).

