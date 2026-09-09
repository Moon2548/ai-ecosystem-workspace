from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List


class PredictRequest(BaseModel):
    """Schema สำหรับรับข้อมูล predict จาก End User"""
    input_data: Dict[str, Any] = Field(
        description="ข้อมูล input — ต้องมี key ''text'' (str) หรือ ''texts'' (list[str])",
        examples=[{"text": "Barack Obama was born in Hawaii."}],
    )
    model_name: Optional[str] = Field(default="bert-base-ner", description="ชื่อ model ใน MLflow Registry")
    model_stage: Optional[str] = Field(default="Production", description="Stage ของ model")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Optional parameters เพิ่มเติม")

    model_config = {"from_attributes": True}


class PredictResponse(BaseModel):
    """Schema response ของ /predict แบบ synchronous (legacy)"""
    prediction: Dict[str, Any]
    model_name: str
    inference_time_ms: float
    request_id: str

    model_config = {"from_attributes": True}


class AsyncPredictResponse(BaseModel):
    """Schema response ของ /predict แบบ async — คืน job_id ให้ client poll ผล"""
    job_id: str = Field(description="Job ID สำหรับตรวจสอบผลลัพธ์ผ่าน GET /inference/jobs/{job_id}")
    status: str = Field(default="queued", description="สถานะ job: queued | processing | completed | failed")
    message: str = Field(default="Job queued successfully")

    model_config = {"from_attributes": True}


class InferenceJobResult(BaseModel):
    """Schema ผลลัพธ์ inference job จาก GET /inference/jobs/{job_id}"""
    job_id: str
    status: str = Field(description="queued | processing | completed | failed | not_found")
    model_name: Optional[str] = None
    model_stage: Optional[str] = None
    inference_time_ms: Optional[float] = None
    input_count: Optional[int] = None
    results: Optional[List[Any]] = Field(default=None, description="ผลลัพธ์ NER entities")
    error: Optional[str] = Field(default=None, description="ข้อความ error (กรณี failed)")

    model_config = {"from_attributes": True}


class ModelInfo(BaseModel):
    """Schema ข้อมูลของ Model"""
    model_name: str
    version: str
    status: str
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class ModelListResponse(BaseModel):
    """Schema รายการ Model ทั้งหมดที่ใช้งานได้"""
    models: List[ModelInfo]
    total: int

    model_config = {"from_attributes": True}


class InferenceHealthResponse(BaseModel):
    """Schema สถานะความพร้อมใช้งานของ Inference Channel"""
    status: str
    available_models: int
    redis_connected: bool
    minio_connected: bool

    model_config = {"from_attributes": True}
