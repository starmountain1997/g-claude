#!/usr/bin/env python3
"""Generate GSM8K dataset for benchmarking."""

import json
import urllib.request
import zipfile
from pathlib import Path

import click
from loguru import logger
from modelscope import snapshot_download
from transformers import AutoTokenizer


@click.command()
@click.option(
    "--input-len", default=64000, show_default=True, help="Input token length"
)
@click.option("--batch-size", default=2800, show_default=True, help="Batch size")
@click.option(
    "--model-id", default="deepseek-ai/DeepSeek-V3", help="Model ID from modelscope"
)
@click.option(
    "--cache-dir", default="./tokenizer_cache", help="Tokenizer cache directory"
)
@click.option("--zip-path", default="./gsm8k.zip", help="Path to GSM8K zip file")
@click.option("--gsm8k-dir", default="./gsm8k", help="GSM8K extracted directory")
def main(
    input_len: int,
    batch_size: int,
    model_id: str,
    cache_dir: str,
    zip_path: str,
    gsm8k_dir: str,
):
    """Generate GSM8K dataset with specified input length and batch size."""
    cache_dir = Path(cache_dir)
    zip_path = Path(zip_path)
    gsm8k_file = Path(gsm8k_dir) / "train.jsonl"
    output_file = Path(f"GSM8K-in{input_len}-bs{batch_size}.jsonl")

    if output_file.exists():
        logger.info(f"Dataset already exists: {output_file}")
        return

    tokenizer_path = download_tokenizer_only(model_id, cache_dir)
    logger.success(f"Tokenizer downloaded to: {tokenizer_path}")

    # Use native Python libraries for downloading and unzipping (OS-independent)
    if not gsm8k_file.exists():
        if not zip_path.exists():
            download_url = "http://opencompass.oss-cn-shanghai.aliyuncs.com/datasets/data/gsm8k.zip"
            logger.info(
                f"'{zip_path}' not found locally. Downloading from {download_url}..."
            )
            try:
                urllib.request.urlretrieve(download_url, zip_path)
                logger.success(f"Successfully downloaded {zip_path}")
            except Exception as e:
                logger.error(f"Download failed: {e}")
                return

        logger.info(f"Unzipping {zip_path}...")
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(zip_path.parent)
        except zipfile.BadZipFile as e:
            logger.error(f"Failed to extract zip file: {e}")
            return

    if not gsm8k_file.exists():
        logger.error(f"Still not found after unzip: {gsm8k_file}")
        return

    tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_path))
    logger.info(f"Loading GSM8K from {gsm8k_file}...")

    # Pythonic list comprehension for file reading
    with gsm8k_file.open("r", encoding="utf-8") as f:
        dataset = [json.loads(line)["question"] for line in f]

    logger.info(f"Processing {len(dataset)} questions...")

    dataset_2k = []
    for sentence in dataset:
        words = tokenizer.tokenize(sentence)
        if not words:
            continue

        # Pythonic list repeating: mathematically determine the multiplier
        multiplier = (input_len // len(words)) + 1
        words = (words * multiplier)[:input_len]

        dataset_2k.append(tokenizer.convert_tokens_to_string(words))

    if not dataset_2k:
        logger.warning("No samples to write to output file. Skipping file creation.")
        return

    # Pythonic list repeating for dataset batch size
    multiplier = (batch_size // len(dataset_2k)) + 1
    dataset_2k = (dataset_2k * multiplier)[:batch_size]

    logger.info(f"Writing {len(dataset_2k)} samples to {output_file}...")

    with output_file.open("w", encoding="utf-8") as f:
        for item in dataset_2k:
            f.write(
                json.dumps({"question": item, "answer": "none"}, ensure_ascii=False)
                + "\n"
            )

    logger.success(f"Done: {output_file}")


def download_tokenizer_only(model_id: str, cache_dir: Path) -> Path:
    """Download tokenizer files only from modelscope."""
    tokenizer_files = [
        "tokenizer_config.json",
        "tokenizer.json",
        "vocab.json",
        "merges.txt",
        "special_tokens_map.json",
        "chat_template.json",
        "config.json",
    ]

    model_path = snapshot_download(
        model_id,
        cache_dir=str(cache_dir),
        ignore_patterns=["*.bin", "*.safetensors", "*.pth", "*.model", "*.gguf"],
        allow_patterns=tokenizer_files,
    )
    return Path(model_path)


if __name__ == "__main__":
    main()
