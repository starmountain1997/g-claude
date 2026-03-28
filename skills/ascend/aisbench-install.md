# AISBench Installation

______________________________________________________________________

## Prerequisites

Python 3.10, 3.11, or 3.12 required (not 3.9 or 3.13+). Check:

```bash
python3 --version
```

______________________________________________________________________

## Install

Ask the user: **where do you want to clone the AISBench repo?** (e.g. `~/tools/benchmark` or `/home/user/third_party/benchmark`)

```bash
git clone https://github.com/AISBench/benchmark.git <target_dir>
cd <target_dir>
pip3 install -e ./ --use-pep517
```

This installs the core package. For evaluating vLLM services (required for this workflow), also install service dependencies:

```bash
pip3 install -r requirements/api.txt
pip3 install -r requirements/extra.txt
```

**Optional extras** — install only if needed:

| Extra | When to install |
| :--- | :--- |
| `requirements/hf_vl_dependency.txt` | HuggingFace VLM / vLLM offline VL inference |
| `requirements/datasets/bfcl_dependencies.txt --no-deps` | BFCL function-calling benchmark |
| `requirements/datasets/ocrbench_v2.txt` | OCRBench_v2 dataset |

______________________________________________________________________

## Verify

```bash
ais_bench -h
```

If the help text prints, installation succeeded.

______________________________________________________________________

## Record the Install Path

After installing, note the source root for future use:

```bash
pip show ais_bench_benchmark
```

The `Editable project location` field is the root used for all config paths (e.g. `configs/datasets/`, `configs/models/`).
