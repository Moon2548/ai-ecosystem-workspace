from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

class PredictRequest(BaseModel):
    """Schema สำหรับรับข้อมูล predict จาก End User"""
    input_data: Dict[str, Any]
    model_name: Optional[str] = "default"
    parameters: Optional[Dict[str, Any]] = None
    
    model_config = {"from_attributes": True}

class PredictResponse(BaseModel):
    """Schema สำหรับส่งผลลัพธ์การ predict กลับไปยัง End User"""
    prediction: Dict[str, Any]
    model_name: str
    inference_time_ms: float
    request_id: str
    
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
