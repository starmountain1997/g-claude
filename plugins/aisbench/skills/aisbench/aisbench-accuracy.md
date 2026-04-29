# AISBench Accuracy Evaluation Guide

AISBench evaluates model accuracy by sending requests to a running vLLM service and comparing outputs against reference answers.

______________________________________________________________________

## Step 1 — Download Dataset

Follow [aisbench-datasets.md](aisbench-datasets.md) to download the dataset. Place files under `$LOCATION/ais_bench/datasets/`.

______________________________________________________________________

## Step 2 — Run

vLLM's `--max-model-len` should be at least `35000` for most datasets.

```bash
# C-Eval
ais_bench --models vllm_api_general_chat --datasets ceval_gen_0_shot_cot_chat_prompt.py --mode all --dump-eval-details --merge-ds

# MMLU
ais_bench --models vllm_api_general_chat --datasets mmlu_gen_0_shot_cot_chat_prompt.py --mode all --dump-eval-details --merge-ds

# GPQA
ais_bench --models vllm_api_general_chat --datasets gpqa_gen_0_shot_str.py --mode all --dump-eval-details --merge-ds

# MATH-500
ais_bench --models vllm_api_general_chat --datasets math500_gen_0_shot_cot_chat_prompt.py --mode all --dump-eval-details --merge-ds

# LiveCodeBench
ais_bench --models vllm_api_general_chat --datasets livecodebench_code_generate_lite_gen_0_shot_chat.py --mode all --dump-eval-details --merge-ds

# AIME 2024
ais_bench --models vllm_api_general_chat --datasets aime2024_gen_0_shot_chat_prompt.py --mode all --dump-eval-details --merge-ds

# GSM8K
ais_bench --models vllm_api_general_chat --datasets gsm8k_gen_0_shot_cot_chat_prompt.py --mode all --dump-eval-details --merge-ds
```

______________________________________________________________________

## Output Structure

Results land in `outputs/default/<timestamp>/`:

```
20250628_151326/
├── configs/                    # Combined config snapshot
├── logs/
│   ├── eval/<model>/           # Accuracy evaluation logs
│   └── infer/<model>/          # Inference logs
├── predictions/<model>/        # Raw model outputs (JSON)
├── results/<model>/            # Per-sample scores
└── summary/
    ├── summary_*.csv           # Final accuracy scores (table)
    ├── summary_*.md            # Final accuracy scores (Markdown)
    └── summary_*.txt           # Final accuracy scores (text)
```

______________________________________________________________________

## Resume / Re-evaluate

```bash
# Re-evaluate without re-running inference (e.g. after fixing answer extraction)
ais_bench --models vllm_api_general_chat --datasets gsm8k_gen --mode eval --reuse 20250628_151326
```

______________________________________________________________________

## Troubleshooting

**Accuracy too low — inspect raw outputs:**

```bash
cat outputs/default/$TS/predictions/vllm-api-general-chat/gsm8k.json | \
  python3 -c "import sys,json; [print(json.loads(l)['prediction'][:200]) for l in sys.stdin]" | head -20
```

- **Truncated output**: raise `max_out_len`; check vLLM `--max-model-len` (needs to exceed 35000)
- **Wrong answer format**: add `pred_postprocessor=dict(type=extract_non_reasoning_content)` for reasoning models (strips `<think>...</think>`)
- **Failed requests**: check `predictions/.../gsm8k_failed.json`; reduce `batch_size` if OOM
