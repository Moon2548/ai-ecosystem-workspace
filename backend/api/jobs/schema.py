from pydantic import BaseModel, Field
from typing import Optional, List

class TrainingJobRequest(BaseModel):
    model_name: str = Field(..., description="ชื่อโมเดลที่ต้องการเทรน")
    dataset_name: str = Field(..., description="ชื่อ dataset ที่ใช้เทรน")
    epochs: int = Field(10, ge=1, le=1000, description="จำนวน epochs")
    batch_size: int = Field(32, ge=1, le=512, description="ขนาด batch")
    learning_rate: float = Field(0.001, gt=0, lt=1, description="Learning rate")
    config: Optional[dict] = Field(None, description="การตั้งค่าเพิ่มเติม")
    description: Optional[str] = Field(None, description="คำอธิบาย job")

class TrainingJobResponse(BaseModel):
    job_id: str
    model_name: str
    dataset_name: str
    status: str
    created_at: str
    message: str

class JobStatusResponse(BaseModel):
    job_id: str
    model_name: str
    status: str # 'queued' | 'running' | 'completed' | 'failed'
    progress_percent: float
    current_epoch: Optional[int] = None
    total_epochs: Optional[int] = None
    created_at: str
    updated_at: str
    error_message: Optional[str] = None

class JobListResponse(BaseModel):
    jobs: List[JobStatusResponse]
    total: int
    page: int
    page_size: int

class JobCancelResponse(BaseModel):
    job_id: str
    status: str
    message: str
