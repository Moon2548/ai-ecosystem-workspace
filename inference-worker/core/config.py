"""
Inference Worker — Core Configuration
อ่านค่า config จาก environment variables
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(ROOT_DIR, ".env")


class Settings(BaseSettings):
    """Inference Worker settings — อ่านจาก .env หรือ environment variables"""

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Redis
    redis_url: str = "redis://localhost:6379"

    # MLflow
    mlflow_tracking_uri: str = "http://localhost:5000"
    mlflow_s3_endpoint_url: str = "http://localhost:9000"
    aws_access_key_id: str = "minioadmin"
    aws_secret_access_key: str = "minioadmin123"

    # Model
    model_name: str = "bert-base-ner"
    model_stage: str = "Production"

    # MinIO (fallback artifact store)
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin123"


settings = Settings()
