"""
ARQ Worker Training Service — Token Classification (NER)
ใช้ BERT fine-tuning บน CoNLL-2003 dataset ตาม HuggingFace Chapter 7/2

Pipeline:
1. ดาวน์โหลด Parquet dataset จาก MinIO
2. โหลด & Tokenize ด้วย bert-base-cased พร้อม label alignment
3. เทรนด้วย HuggingFace Trainer API
4. อัพโหลด trained model กลับไป MinIO พร้อม versioning
"""

import os
import tempfile
import logging
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import evaluate
from minio import Minio
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification,
    TrainingArguments,
    Trainer,
    DataCollatorForTokenClassification,
)

logger = logging.getLogger(__name__)

# NER label names สำหรับ CoNLL-2003
label_names = [
    "O", "B-PER", "I-PER", "B-ORG", "I-ORG",
    "B-LOC", "I-LOC", "B-MISC", "I-MISC",
]


def get_minio_client() -> Minio:
    """สร้าง MinIO client จาก environment variables"""
    endpoint = os.environ.get("MINIO_ENDPOINT", "minio:9000")
    # ตัด http:// หรือ https:// ออกถ้ามี
    endpoint = endpoint.replace("http://", "").replace("https://", "")
    return Minio(
        endpoint,
        access_key=os.environ.get("MINIO_ACCESS_KEY", "minioadmin"),
        secret_key=os.environ.get("MINIO_SECRET_KEY", "minioadmin123"),
        secure=False,
    )


def tokenize_and_align_labels(examples, tokenizer):
    """
    Tokenize และจัดการ label alignment สำหรับ subword tokens
    - Special tokens ([CLS], [SEP]) → label = -100 (ignored)
    - First subword ของคำ → ได้ label ของคำนั้น
    - Subsequent subwords → label = -100 (ignored)
    """
    tokenized_inputs = tokenizer(
        examples["tokens"], truncation=True, is_split_into_words=True
    )
    labels = []
    for i, label in enumerate(examples["ner_tags"]):
        word_ids = tokenized_inputs.word_ids(batch_index=i)
        previous_word_idx = None
        label_ids = []
        for word_idx in word_ids:
            if word_idx is None:
                label_ids.append(-100)
            elif word_idx != previous_word_idx:
                label_ids.append(label[word_idx])
            else:
                label_ids.append(-100)
            previous_word_idx = word_idx
        labels.append(label_ids)
    tokenized_inputs["labels"] = labels
    return tokenized_inputs


async def train_model(
    ctx,
    dataset_name: str = "conll2003",
    model_name: str = "bert-base-ner",
    epochs: int = 3,
    batch_size: int = 8,
    learning_rate: float = 2e-5,
):
    """
    ARQ Job Function สำหรับเทรน Token Classification Model

    ขั้นตอน:
    1. ดาวน์โหลด Parquet files จาก MinIO bucket 'datasets'
    2. โหลด dataset จาก parquet files
    3. Tokenize ด้วย bert-base-cased + label alignment
    4. เทรนด้วย HuggingFace Trainer API
    5. อัพโหลด model + log ไป MinIO bucket 'models' พร้อม versioning
    """
    logger.info(f"Starting train_model job: model={model_name}, dataset={dataset_name}")
    minio_client = get_minio_client()

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        dataset_dir = tmp_path / "dataset"
        dataset_dir.mkdir()
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # ===== Step 1: ดาวน์โหลด Parquet files จาก MinIO =====
        logger.info(f"Downloading dataset '{dataset_name}' from MinIO...")
        objects = minio_client.list_objects(
            "datasets", prefix=f"{dataset_name}/", recursive=True
        )
        data_files = {}
        for obj in objects:
            file_name = Path(obj.object_name).name
            local_file = dataset_dir / file_name
            minio_client.fget_object("datasets", obj.object_name, str(local_file))
            split = file_name.replace(".parquet", "")
            data_files[split] = str(local_file)
            logger.info(f"  Downloaded: {obj.object_name}")

        if not data_files:
            raise ValueError(
                f"No parquet files found in MinIO bucket 'datasets/{dataset_name}/'"
            )

        # ===== Step 2: โหลด dataset จาก parquet =====
        logger.info(f"Loading dataset from parquet: {list(data_files.keys())}")
        raw_datasets = load_dataset("parquet", data_files=data_files)
        logger.info(f"Dataset loaded: {raw_datasets}")

        # ===== Step 3: เตรียม Tokenizer & Model =====
        model_checkpoint = "bert-base-cased"
        tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
        model = AutoModelForTokenClassification.from_pretrained(
            model_checkpoint,
            num_labels=len(label_names),
            id2label={i: l for i, l in enumerate(label_names)},
            label2id={l: i for i, l in enumerate(label_names)},
        )
        logger.info(f"Model & tokenizer loaded: {model_checkpoint}")

        # ===== Step 4: Tokenize dataset =====
        tokenized_datasets = raw_datasets.map(
            lambda examples: tokenize_and_align_labels(examples, tokenizer),
            batched=True,
            remove_columns=raw_datasets["train"].column_names,
        )
        logger.info("Dataset tokenized with label alignment")

        # ===== Step 5: เตรียม Evaluation Metric =====
        metric = evaluate.load("seqeval")

        def compute_metrics(eval_preds):
            logits, labels = eval_preds
            predictions = np.argmax(logits, axis=-1)
            true_labels = [
                [label_names[l] for l in label if l != -100]
                for label in labels
            ]
            true_predictions = [
                [label_names[p] for (p, l) in zip(prediction, label) if l != -100]
                for prediction, label in zip(predictions, labels)
            ]
            results = metric.compute(
                predictions=true_predictions, references=true_labels
            )
            return {
                "precision": results["overall_precision"],
                "recall": results["overall_recall"],
                "f1": results["overall_f1"],
                "accuracy": results["overall_accuracy"],
            }

        # ===== Step 6: Setup logging to file =====
        log_file = output_dir / "train.log"
        fh = logging.FileHandler(str(log_file))
        fh.setLevel(logging.INFO)
        fh.setFormatter(
            logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
        )
        logger.addHandler(fh)

        # ===== Step 7: เทรนโมเดล =====
        training_args = TrainingArguments(
            output_dir=str(output_dir),
            eval_strategy="epoch",
            save_strategy="epoch",
            learning_rate=learning_rate,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            num_train_epochs=epochs,
            weight_decay=0.01,
            logging_steps=50,
            load_best_model_at_end=True,
            metric_for_best_model="f1",
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_datasets["train"],
            eval_dataset=tokenized_datasets.get(
                "validation", tokenized_datasets.get("test")
            ),
            data_collator=DataCollatorForTokenClassification(tokenizer=tokenizer),
            compute_metrics=compute_metrics,
            processing_class=tokenizer,
        )

        logger.info("Training started...")
        trainer.train()
        logger.info("Training completed")

        # ===== Step 8: บันทึก model =====
        trainer.save_model(str(output_dir))
        tokenizer.save_pretrained(str(output_dir))

        # ===== Step 9: อัพโหลดไป MinIO พร้อม Versioning =====
        version = f"v{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        minio_prefix = f"{model_name}/{version}"

        if not minio_client.bucket_exists("models"):
            minio_client.make_bucket("models")

        logger.info(f"Uploading model to MinIO: models/{minio_prefix}")
        for f in output_dir.rglob("*"):
            if f.is_file():
                rel_path = f.relative_to(output_dir).as_posix()
                object_name = f"{minio_prefix}/{rel_path}"
                minio_client.fput_object("models", object_name, str(f))
                logger.info(f"  Uploaded: models/{object_name}")

        logger.info(f"Training job completed. Model saved to: models/{minio_prefix}")
        logger.removeHandler(fh)
        fh.close()

        return {
            "status": "completed",
            "model_name": model_name,
            "version": version,
            "minio_path": f"models/{minio_prefix}",
        }
