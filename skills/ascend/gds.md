# gDS: Benchmarking & Configuration Toolkit

## Custom Dataset Generation (GSM8K)

For automated dataset preparation and generation, use the provided script which handles downloading (via OpenCompass), unzipping, and truncating/repeating samples to reach target input lengths and batch sizes.

**Requirements**: `pip install click loguru modelscope transformers`

```bash
# Generate a dataset with specific input length and batch size
python ${CLAUDE_SKILL_DIR}/scripts/make_gsm8k.py \
    --input-len 64000 \
    --batch-size 2800 \
    --model-id deepseek-ai/DeepSeek-V3
```

- **`--input-len`**: Target token count per sample (repeats text if too short).
- **`--batch-size`**: Total number of samples in the output file.
- **`--model-id`**: Used to download the appropriate tokenizer for token counting.
- **`--zip-path`**: Path to the GSM8K zip file (default: `./gsm8k.zip`).

If the zip file is not found at `--zip-path`, the script automatically downloads it from:
`http://opencompass.oss-cn-shanghai.aliyuncs.com/datasets/data/gsm8k.zip`

## Core Features
...
- **AISBench Automation**: Utilities for managing `ais-bench` benchmarks, parsing results, and triggering tests.
- **Config Generator**: Automated generation of model description and benchmark configuration files (JSON/YAML).
- **GitHub Action Watcher**: Monitoring tools for CI/CD pipelines, ideal for performance regression tracking.
- **Data Validation**: Tools for verifying benchmark values and performance metrics.

## Workflow Integration

`gDS` is typically used to bridge the gap between model deployment and automated performance validation.

1. **Configure**: Use `config_generator` to create the necessary benchmark description files.
2. **Execute**: Run `aisbench_tools` to trigger performance tests on Ascend hardware.
3. **Monitor**: Track progress and regressions via the GitHub action watcher.

## Common Usage

```bash
# Example: Generate an AISBench config
python -m gds.config_generator --model <MODEL_PATH> --output config.json

# Example: Run benchmarks and parse results
python -m gds.aisbench_tools.runner --config config.json
```
