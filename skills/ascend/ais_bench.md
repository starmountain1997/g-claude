# AISBench Evaluation Protocol

Protocol for running GSM8K accuracy and performance benchmarks against a running vLLM-Ascend service.

## 0. Prerequisites

- A vLLM-Ascend service must be **already running** (see [vllm-run.md](vllm-run.md)).
- The service must be accessible at a known endpoint (e.g., `http://localhost:8000`).

## 1. Install AISBench

```bash
pip install ais_bench
```

## 2. Run GSM8K Evaluation

```bash
ais_bench \
  --model <MODEL_NAME> \
  --backend vllm \
  --url http://localhost:8000 \
  --dataset gsm8k \
  --num_fewshot 0 \
  --batch_size 8
```

## 3. Interpret Results

- **Accuracy threshold**: ≤ 1 percentage point drop vs FP16 baseline is considered PASS.
- If accuracy falls outside the threshold, proceed to [sensitivity-analysis.md](sensitivity-analysis.md) for accuracy recovery.
