# AISBench Evaluation Guide

AISBench is an [OpenCompass](https://github.com/open-compass/opencompass)-based evaluation framework for both accuracy and performance benchmarking of LLM services.

______________________________________________________________________

## Installation

```bash
cd third_party/benchmark
pip3 install -e ./ --use-pep517
```

Python 3.10 or 3.11 required.

______________________________________________________________________

## Common Setup

**Artifact Storage**: Save all generated evaluation config files to the current working directory. Do not save them elsewhere.

Before running any evaluation, ask the user:

- **vLLM port** — e.g. `8080`
- **Model-served-name** — the name shown by `curl http://localhost:<port>/v1/models`

All configs below use `VLLMCustomAPIChatStream` (`vllm_api_stream_chat`). `batch_size` maps directly to `ThreadPoolExecutor(max_workers=batch_size)` — it is the number of concurrent requests sent to vLLM.

______________________________________________________________________

## Accuracy Evaluation (GSM8K)

GSM8K (math word problems) is the recommended accuracy proxy for pure-language models — it is sensitive to quantization-induced reasoning degradation and runs quickly (~1319 samples).

**Write `gsm8k_eval.py`** with the user's port and model-served-name. Set `batch_size=32` for fast evaluation; raise to 64 if the server has spare capacity:

```python
from mmengine.config import read_base
from ais_bench.benchmark.models import VLLMCustomAPIChatStream
from ais_bench.benchmark.utils.model_postprocessors import extract_non_reasoning_content

with read_base():
    from ais_bench.benchmark.configs.datasets.gsm8k.gsm8k_gen_0_shot_cot_chat_prompt import gsm8k_datasets

models = [
    dict(
        attr="service",
        type=VLLMCustomAPIChatStream,
        abbr='vllm-api-stream-chat',
        path="",
        model="<MODEL_SERVED_NAME>",   # fill in
        request_rate=0,
        retry=2,
        host_ip="localhost",
        host_port=8080,                # fill in
        max_out_len=1024,
        batch_size=32,                 # concurrent requests — raise if server allows
        trust_remote_code=False,
        generation_kwargs=dict(
            temperature=0.0,
            top_k=1,
            top_p=1.0,
            seed=42,
            repetition_penalty=1.0,
        ),
        pred_postprocessor=dict(type=extract_non_reasoning_content)
    )
]

datasets = gsm8k_datasets
```

**Run** from the benchmark repo root:

```bash
ais_bench gsm8k_eval.py --mode all -w ./eval_output
```

Results appear in `eval_output/summary/summary_*.txt`. Check the `gsm8k` accuracy row.

**Acceptance threshold**: ≤ 1 percentage point drop vs. FP16 baseline. Larger drops indicate the quantization config needs further tuning.

______________________________________________________________________

## Performance Testing (GSM8K)

Measures throughput and latency after quantization. Key differences from accuracy eval:

- `ignore_eos=True` — forces output to reach `max_out_len`, giving consistent token counts across requests
- `batch_size` — sweep (1 → 4 → 16 → 32) to find the throughput knee
- Dataset: `gsm8k_gen_0_shot_cot_str_perf` (simplified prompt, no CoT, focused on token throughput)

**Write `gsm8k_perf.py`**:

```python
from mmengine.config import read_base
from ais_bench.benchmark.models import VLLMCustomAPIChatStream
from ais_bench.benchmark.utils.model_postprocessors import extract_non_reasoning_content

with read_base():
    from ais_bench.benchmark.configs.datasets.gsm8k.gsm8k_gen_0_shot_cot_str_perf import gsm8k_datasets

models = [
    dict(
        attr="service",
        type=VLLMCustomAPIChatStream,
        abbr='vllm-api-stream-chat',
        path="",
        model="<MODEL_SERVED_NAME>",   # fill in
        request_rate=0,
        retry=2,
        host_ip="localhost",
        host_port=8080,                # fill in
        max_out_len=512,
        batch_size=16,                 # start here; double until throughput plateaus
        trust_remote_code=False,
        generation_kwargs=dict(
            temperature=1.0,
            top_k=1,
            top_p=1.0,
            seed=42,
            repetition_penalty=1.0,
            ignore_eos=True,           # must be True for consistent output length
        ),
        pred_postprocessor=dict(type=extract_non_reasoning_content)
    )
]

datasets = gsm8k_datasets
```

**Run** from the benchmark repo root:

```bash
ais_bench gsm8k_perf.py --mode perf -w ./perf_output
```

**Key metrics** (printed to console and saved in `perf_output/performance/`):

| Metric | What it measures | Quantized vs FP16 target |
| :--- | :--- | :--- |
| `TTFT` | Prefill latency (Time to First Token) | Similar or lower |
| `TPOT` / `ITL` | Decode speed (ms per output token) | Lower (faster) |
| `Output Token Throughput` | tokens/s | Higher |
| `E2EL` | Full request latency | Lower |

______________________________________________________________________

## Multimodal Model Evaluation (VLM)

GSM8K is text-only and cannot test vision capability. Use a VLM-specific benchmark instead.

### Recommended benchmarks

| Benchmark | What it tests | Sample count | When to use |
| :--- | :--- | :--- | :--- |
| **MMBench** | General visual understanding, reasoning, OCR | ~3000 | Primary accuracy proxy — broad coverage |
| **TextVQA** | Text recognition in natural images | ~5000 | If the model targets document/scene-text tasks |
| **OCRBench** | OCR and document understanding | ~1000 | Document/receipt/formula models |
| **MMMU** | College-level multi-discipline VQA | ~11500 | Comprehensive capability; slow but thorough |

**Recommendation**: Start with MMBench. It runs in ~15 minutes at `batch_size=16` and is the de-facto standard for Chinese VLM evaluation.

**Acceptance threshold**: ≤ 1 percentage point drop on the overall score vs. FP16 baseline (same rule as GSM8K).

### Accuracy Evaluation (MMBench)

The same `VLLMCustomAPIChatStream` model class is used — it sends requests through the OpenAI-compatible API, and vLLM's vision-capable endpoint handles the image inputs transparently.

**Key differences from text-only eval**:

- `max_out_len` — set to `256` (VLM answers are typically short)
- `batch_size` — use `8` or `16`; vision encoding is memory-intensive and high concurrency causes OOM on the server side
- Dataset import path — use the VLM dataset config, not `gsm8k`

**Write `mmbench_eval.py`**:

```python
from mmengine.config import read_base
from ais_bench.benchmark.models import VLLMCustomAPIChatStream
from ais_bench.benchmark.utils.model_postprocessors import extract_non_reasoning_content

with read_base():
    from ais_bench.benchmark.configs.datasets.mmbench.mmbench_gen import mmbench_datasets

models = [
    dict(
        attr="service",
        type=VLLMCustomAPIChatStream,
        abbr='vllm-api-stream-chat',
        path="",
        model="<MODEL_SERVED_NAME>",   # fill in
        request_rate=0,
        retry=2,
        host_ip="localhost",
        host_port=8080,                # fill in
        max_out_len=256,               # shorter than text eval — VLM answers are brief
        batch_size=8,                  # lower than text eval — vision encoding is memory-intensive
        trust_remote_code=False,
        generation_kwargs=dict(
            temperature=0.0,
            top_k=1,
            top_p=1.0,
            seed=42,
            repetition_penalty=1.0,
        ),
        pred_postprocessor=dict(type=extract_non_reasoning_content)
    )
]

datasets = mmbench_datasets
```

**Run**:

```bash
ais_bench mmbench_eval.py --mode all -w ./eval_output
```

Results appear in `eval_output/summary/summary_*.txt`. Check the `mmbench` overall accuracy row.

> **Verify the import path before running.** The dataset config path (`ais_bench.benchmark.configs.datasets.mmbench.mmbench_gen`) depends on the installed AISBench version. Run `python -c "import ais_bench; print(ais_bench.__file__)"` to find the install root, then browse `configs/datasets/` to confirm the exact module name.

### vLLM Prerequisites for Vision Inputs

Serving a VLM requires additional vLLM flags. Confirm the model is running with vision support before evaluating:

```bash
curl http://localhost:8080/v1/chat/completions \
	-H "Content-Type: application/json" \
	-d '{
    "model": "<MODEL_SERVED_NAME>",
    "messages": [{"role": "user", "content": [
      {"type": "text", "text": "describe this image in one word"},
      {"type": "image_url", "image_url": {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/240px-PNG_transparency_demonstration_1.png"}}
    ]}],
    "max_tokens": 20
  }'
```

If the response contains a description (not an error), vision inputs are working. If it errors, check that `--max-num-seqs` and `--image-input-type` are set correctly in the vLLM launch command — see `vllm-run.md`.

### Performance Testing (VLM)

Use a multimodal prompt set for perf testing. Replace the GSM8K performance dataset with a VLM-specific one and keep `ignore_eos=True`:

```python
with read_base():
    from ais_bench.benchmark.configs.datasets.mmbench.mmbench_gen_perf import mmbench_datasets  # verify path
```

**Run**:

```bash
ais_bench mmbench_perf.py --mode perf -w ./perf_output
```

The same latency metrics apply (`TTFT`, `TPOT`, `E2EL`). Vision models will show higher TTFT than equivalent text models due to image pre-processing — this is expected, not a regression.
