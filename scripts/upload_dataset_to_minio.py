"""
Download HuggingFace dataset (e.g. conll2003) and upload to MinIO as parquet files.

Usage:
    uv run python scripts/upload_dataset_to_minio.py
    uv run python scripts/upload_dataset_to_minio.py --dataset conll2003
"""

import os
import argparse
import tempfile
from pathlib import Path
from datasets import load_dataset
from minio import Minio


def upload_dataset(dataset_name: str):
    # 1. MinIO config from environment variables
    raw_endpoint = (
        os.environ.get("MINIO_ENDPOINT")
        or os.environ.get("Minio_Endpoint")
        or "localhost:9000"
    )
    access_key = (
        os.environ.get("MINIO_ACCESS_KEY")
        or os.environ.get("Minio_Access_Key")
        or "minioadmin"
    )
    secret_key = (
        os.environ.get("MINIO_SECRET_KEY")
        or os.environ.get("Minio_Secret_Key")
        or "minioadmin123"
    )
    bucket_name = "datasets"

    endpoint = raw_endpoint.replace("http://", "").replace("https://", "")

    # 2. Connect MinIO
    client = Minio(
        endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=False,
    )

    # 3. Create bucket if not exists
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        print(f"Created bucket '{bucket_name}'")
    else:
        print(f"Bucket '{bucket_name}' already exists")

    # 4. Download dataset from Hugging Face
    # conll2003 was moved from the old Hub, use eriktks/conll2003 instead
    hf_name = dataset_name
    if dataset_name == "conll2003":
        hf_name = "eriktks/conll2003"
    print(f"Downloading dataset '{hf_name}' from Hugging Face...")
    try:
        ds = load_dataset(hf_name, trust_remote_code=True)
    except (TypeError, RuntimeError):
        ds = load_dataset(hf_name)
    print(f"Download complete: {ds}")

    # 5. Convert to Parquet and upload to MinIO
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        print("Converting dataset to parquet...")

        for split in ds.keys():
            parquet_file = tmp_path / f"{split}.parquet"
            ds[split].to_parquet(str(parquet_file))

            object_name = f"{dataset_name}/{split}.parquet"
            file_size = parquet_file.stat().st_size
            print(f"  Uploading: {object_name} ({file_size:,} bytes)")
            client.fput_object(bucket_name, object_name, str(parquet_file))

    print(f'\nDataset "{dataset_name}" uploaded to MinIO bucket "{bucket_name}" successfully!')
    print(f"  Format: parquet")
    print(f"  Splits: {list(ds.keys())}")
    print(f"  Path: {bucket_name}/{dataset_name}/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download HuggingFace dataset and upload to MinIO as parquet"
    )
    parser.add_argument(
        "--dataset",
        default="conll2003",
        help="Dataset name on Hugging Face (default: conll2003)",
    )
    args = parser.parse_args()
    upload_dataset(args.dataset)
