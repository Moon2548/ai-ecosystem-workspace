from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class QueueTrainRequest(BaseModel):
    """Request body สำหรับสร้าง Training Job เข้าคิว"""
    dataset_name: str = Field("conll2003", description="ชื่อ dataset ใน MinIO bucket 'datasets'")
    model_name: str = Field("bert-base-ner", description="ชื่อโมเดลที่ต้องการเทรน (ใช้เป็น prefix ใน MinIO)")
    epochs: int = Field(3, ge=1, le=100, description="จำนวน epochs")
    batch_size: int = Field(8, ge=1, le=128, description="ขนาด batch")
    learning_rate: float = Field(2e-5, gt=0, lt=1, description="Learning rate")
    start_time: Optional[datetime] = Field(
        None,
        description="เวลาที่กำหนดให้เริ่มเทรน (ISO 8601 format) ถ้าไม่ระบุจะเริ่มทันที"
    )


class QueueTrainResponse(BaseModel):
    """Response body สำหรับ Training Job ที่ถูกสร้าง"""
    job_id: str
    status: str
    message: str
