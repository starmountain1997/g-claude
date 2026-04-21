# AISBench Performance Evaluation Guide

This guide covers performance benchmarking (throughput, latency, concurrency) for LLM services on Ascend NPUs using AISBench.

______________________________________________________________________

## Custom Dataset Generation (GSM8K)

For performance benchmarking, you often need datasets with specific token lengths and batch sizes. Use the provided script to automate downloading (via OpenCompass), unzipping, and truncating/repeating samples.

**Requirements**: `pip install click loguru modelscope transformers`

### Command Reference

```bash
# Generate a dataset with specific input length and batch size
python ${CLAUDE_SKILL_DIR}/scripts/make_gsm8k.py \
    --input-len 64000 \
    --batch-size 2800 \
    --model-id deepseek-ai/DeepSeek-V3 \
    --zip-path ./gsm8k.zip
```

**Common Options**:
- `--input-len`: Target token count per sample (repeats text if too short).
- `--batch-size`: Total number of samples in the output file.
- `--model-id`: Used to download the appropriate tokenizer for token counting.
- `--zip-path`: Path to the GSM8K zip file (default: `./gsm8k.zip`).

If the zip file is not found at `--zip-path`, the script automatically downloads it from:
`http://opencompass.oss-cn-shanghai.aliyuncs.com/datasets/data/gsm8k.zip`

______________________________________________________________________

## Performance Benchmarking Workflow

... (Rest of performance benchmarking content) ...
