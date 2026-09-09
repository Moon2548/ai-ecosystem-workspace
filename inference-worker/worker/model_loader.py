"""
Model Loader — โหลด trained model จาก MLflow Model Registry
มี cache ในหน่วยความจำ เพื่อไม่ต้องโหลดซ้ำทุก request

ขั้นตอน:
1. เชื่อมต่อ MLflow tracking server
2. ดึง model URI จาก Model Registry (Production stage)
3. โหลด model ด้วย mlflow.transformers.load_model()
4. Fallback → โหลดจาก HuggingFace Hub ถ้า MLflow ยังไม่มีโมเดล
"""

import logging
from typing import Optional

import mlflow
import mlflow.transformers
from transformers import pipeline, Pipeline

from core.config import settings

logger = logging.getLogger(__name__)

# Cache: เก็บ loaded model ไว้ใน memory
_model_cache: dict[str, Pipeline] = {}


def _build_model_uri(model_name: str, stage: str) -> str:
    """สร้าง MLflow model URI สำหรับ Production stage"""
    return f"models:/{model_name}/{stage}"


def load_model(model_name: Optional[str] = None, stage: Optional[str] = None) -> Pipeline:
    """
    โหลด model จาก MLflow Model Registry
    ถ้าโหลดไม่ได้ (ยังไม่มี registered model) จะ fallback ไปใช้ bert-base-cased จาก HuggingFace

    Args:
        model_name: ชื่อ model ใน MLflow Registry (default: จาก settings)
        stage: stage ของ model เช่น Production, Staging (default: จาก settings)

    Returns:
        HuggingFace Pipeline พร้อมใช้งาน
    """
    model_name = model_name or settings.model_name
    stage = stage or settings.model_stage
    cache_key = f"{model_name}:{stage}"

    # ถ้า cache มีอยู่แล้ว ใช้เลย
    if cache_key in _model_cache:
        logger.info(f"Using cached model: {cache_key}")
        return _model_cache[cache_key]

    # ตั้งค่า MLflow
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)

    # ตั้งค่า S3/MinIO endpoint สำหรับ artifact download
    import os
    os.environ["MLFLOW_S3_ENDPOINT_URL"] = settings.mlflow_s3_endpoint_url
    os.environ["AWS_ACCESS_KEY_ID"] = settings.aws_access_key_id
    os.environ["AWS_SECRET_ACCESS_KEY"] = settings.aws_secret_access_key

    model_uri = _build_model_uri(model_name, stage)
    logger.info(f"Loading model from MLflow: {model_uri}")

    try:
        # โหลด model จาก MLflow (คืน HuggingFace pipeline โดยตรง)
        inference_pipeline: Pipeline = mlflow.transformers.load_model(model_uri)
        logger.info(f"Model loaded successfully from MLflow: {model_uri}")

    except Exception as e:
        logger.warning(
            f"Cannot load model from MLflow ({e}). "
            f"Falling back to HuggingFace Hub: bert-base-cased (NER)"
        )
        # Fallback: โหลดจาก HuggingFace Hub
        inference_pipeline = pipeline(
            task="token-classification",
            model="dslim/bert-base-NER",
            aggregation_strategy="simple",
        )
        logger.info("Fallback model loaded: dslim/bert-base-NER")

    # เก็บ cache
    _model_cache[cache_key] = inference_pipeline
    return inference_pipeline


def clear_cache():
    """ล้าง model cache (สำหรับ reload model ใหม่)"""
    _model_cache.clear()
    logger.info("Model cache cleared")
