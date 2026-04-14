# Model Download

Before running any inference or quantization task, download the model to local storage. Always use a local path — never pass a HuggingFace repo ID or ModelScope model ID directly to vLLM or msmodelslim.

## Step 0 — Ask Where to Store

**Before downloading anything**, ask the user:

> "Where do you want to store the model? (e.g. `/data/models` or `/home/user/models`)"

Do not proceed until you have a confirmed `$MODEL_DIR`. All models go under this directory:

```
$MODEL_DIR/<model-name>/
```

______________________________________________________________________

## Step 1 — Try ModelScope First

ModelScope has better connectivity in mainland China and mirrors most major open-source models.

### Check if modelscope is installed

```bash
pip show modelscope
```

If not installed:

```bash
pip install modelscope
```

### Download

```bash
modelscope download \
    --model <MODELSCOPE_MODEL_ID> \
    --local_dir "$MODEL_DIR/<model-name>"
```

**Finding the ModelScope model ID**: It follows the pattern `<organization>/<model-name>`, e.g.:
- `Qwen/Qwen3-32B`
- `deepseek-ai/DeepSeek-R1`
- `ZhipuAI/glm-4-9b-chat`

If the user provides only a HuggingFace model ID, search for the equivalent on ModelScope: the organization and model name are usually identical or very close.

### Verify download

```bash
ls "$MODEL_DIR/<model-name>"
# Must contain: config.json + tokenizer files + weight files (*.safetensors or *.bin)
```

______________________________________________________________________

## Step 2 — Fallback: HuggingFace

Use this only if ModelScope does not have the model or the download fails.

### Check if huggingface_hub is installed

```bash
pip show huggingface_hub
```

If not installed:

```bash
pip install huggingface_hub
```

### Download

```bash
huggingface-cli download \
    <HF_MODEL_ID> \
    --local-dir "$MODEL_DIR/<model-name>" \
    --local-dir-use-symlinks False
```

If the download is interrupted, rerun the same command — `huggingface-cli` resumes from where it left off.

### HuggingFace mirror (if direct access is slow)

```bash
export HF_ENDPOINT=https://hf-mirror.com
huggingface-cli download \
    <HF_MODEL_ID> \
    --local-dir "$MODEL_DIR/<model-name>" \
    --local-dir-use-symlinks False
```

______________________________________________________________________

## Step 3 — Record the Local Path

Once the download is complete, confirm the exact local path with the user and record it as `$MODEL_PATH`:

```bash
# Confirm the path is correct and weights are present
ls "$MODEL_DIR/<model-name>"/*.safetensors 2>/dev/null || ls "$MODEL_DIR/<model-name>"/*.bin
```

From this point on, use `$MODEL_PATH = "$MODEL_DIR/<model-name>"` everywhere — in vLLM launch commands, msmodelslim quantization, and AISBench evaluation configs. Never substitute the online model ID.
