# msmodeling Installation

## Clone the Repository

```bash
git clone https://gitcode.com/Ascend/msmodeling.git
cd msmodeling
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

> If you run tools outside the msmodeling directory, set `PYTHONPATH` first:
>
> ```bash
> export PYTHONPATH=/path/to/msmodeling:$PYTHONPATH
> ```
>
> To read model configs from Hugging Face, set:
>
> ```bash
> export HF_ENDPOINT="https://hf-mirror.com"
> ```
