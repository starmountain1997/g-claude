# AISBench Dataset Download Guide

All dataset files go under `$LOCATION/ais_bench/datasets/` where `$LOCATION` is the AISBench editable install path (`pip show ais_bench_benchmark` → `Editable project location`).

Each dataset also has a README with additional notes:

```bash
cat $LOCATION/ais_bench/benchmark/configs/datasets/<dataset>/README.md
```

______________________________________________________________________

## Text Datasets

**C-Eval:**

```bash
cd $LOCATION/ais_bench/datasets
mkdir -p ceval/formal_ceval && cd ceval/formal_ceval
wget https://www.modelscope.cn/datasets/opencompass/ceval-exam/resolve/master/ceval-exam.zip
unzip ceval-exam.zip && rm ceval-exam.zip
```

**MMLU:**

```bash
cd $LOCATION/ais_bench/datasets
wget http://opencompass.oss-cn-shanghai.aliyuncs.com/datasets/data/mmlu.zip
unzip mmlu.zip && rm mmlu.zip
```

**GPQA:**

```bash
cd $LOCATION/ais_bench/datasets
wget http://opencompass.oss-cn-shanghai.aliyuncs.com/datasets/data/gpqa.zip
unzip gpqa.zip && rm gpqa.zip
```

**MATH-500:**

```bash
cd $LOCATION/ais_bench/datasets
wget http://opencompass.oss-cn-shanghai.aliyuncs.com/datasets/data/math.zip
unzip math.zip && rm math.zip
```

**LiveCodeBench:**

```bash
cd $LOCATION/ais_bench/datasets
git lfs install
git clone https://huggingface.co/datasets/livecodebench/code_generation_lite
```

**AIME 2024:**

```bash
cd $LOCATION/ais_bench/datasets
mkdir -p aime && cd aime
wget http://opencompass.oss-cn-shanghai.aliyuncs.com/datasets/data/aime.zip
unzip aime.zip && rm aime.zip
```

**GSM8K:**

```bash
cd $LOCATION/ais_bench/datasets
wget http://opencompass.oss-cn-shanghai.aliyuncs.com/datasets/data/gsm8k.zip
unzip gsm8k.zip && rm gsm8k.zip
```

______________________________________________________________________

## Multi-Modal Datasets

**TextVQA** (images + text, for multi-modal performance benchmarking):

```bash
cd $LOCATION/ais_bench/datasets
git lfs install
git clone https://huggingface.co/datasets/maoxx241/textvqa_subset
mv textvqa_subset/ textvqa/
mkdir textvqa/textvqa_json/
mv textvqa/*.json textvqa/textvqa_json/
mv textvqa/*.jsonl textvqa/textvqa_json/
```

After download, fix relative image paths to absolute or you'll get a pydantic validation error at runtime:

```bash
cd $LOCATION/ais_bench/datasets/textvqa/textvqa_json
sed -i 's#data/textvqa/train_images/#/absolute/path/to/ais_bench/datasets/textvqa/train_images/#g' textvqa_val.json
```

Replace `/absolute/path/to/ais_bench/datasets/` with the actual path on your machine.

______________________________________________________________________

## Synthetic Dataset (Performance Testing)

No download needed — configure `$LOCATION/ais_bench/datasets/synthetic/synthetic_config.py` directly to control input/output sequence lengths:

```python
synthetic_config = {
    "Type": "string",
    "RequestCount": 1000,
    "StringConfig": {
        "Input":  {"Method": "uniform", "Params": {"MinValue": 512, "MaxValue": 2048}},
        "Output": {"Method": "uniform", "Params": {"MinValue": 128, "MaxValue": 512}},
    }
}
```

Use with `--datasets synthetic_gen` in performance runs.
