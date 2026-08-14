import uuid
from datetime import datetime, timezone
from .schema import (
    TrainingJobRequest, TrainingJobResponse, JobStatusResponse,
    JobListResponse, JobCancelResponse
)

class JobService:
    async def create_training_job(self, request: TrainingJobRequest) -> TrainingJobResponse:
        job_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        return TrainingJobResponse(
            job_id=job_id,
            model_name=request.model_name,
            dataset_name=request.dataset_name,
            status="queued",
            created_at=now,
            message="Training job created and queued successfully"
        )
        
    async def get_job_status(self, job_id: str) -> JobStatusResponse:
        now = datetime.now(timezone.utc).isoformat()
        return JobStatusResponse(
            job_id=job_id,
            model_name="mock_model_v1",
            status="running",
            progress_percent=50.0,
            current_epoch=5,
            total_epochs=10,
            created_at=now,
            updated_at=now
        )
        
    async def list_jobs(self, page: int = 1, page_size: int = 10) -> JobListResponse:
        now = datetime.now(timezone.utc).isoformat()
        jobs = [
            JobStatusResponse(
                job_id=str(uuid.uuid4()),
                model_name="model_1",
                status="completed",
                progress_percent=100.0,
                current_epoch=10,
                total_epochs=10,
                created_at=now,
                updated_at=now
            ),
            JobStatusResponse(
                job_id=str(uuid.uuid4()),
                model_name="model_2",
                status="running",
                progress_percent=30.0,
                current_epoch=3,
                total_epochs=10,
                created_at=now,
                updated_at=now
            ),
            JobStatusResponse(
                job_id=str(uuid.uuid4()),
                model_name="model_3",
                status="queued",
                progress_percent=0.0,
                current_epoch=0,
                total_epochs=20,
                created_at=now,
                updated_at=now
            )
        ]
        return JobListResponse(
            jobs=jobs,
            total=3,
            page=page,
            page_size=page_size
        )
        
    async def cancel_job(self, job_id: str) -> JobCancelResponse:
        return JobCancelResponse(
            job_id=job_id,
            status="cancelled",
            message="Training job has been cancelled"
        )
