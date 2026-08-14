from fastapi import Depends
from .schema import (
    TrainingJobRequest, TrainingJobResponse, JobStatusResponse,
    JobListResponse, JobCancelResponse
)
from .service import JobService

def get_job_service() -> JobService:
    return JobService()

async def create_training_job(
    payload: TrainingJobRequest,
    service: JobService = Depends(get_job_service)
) -> TrainingJobResponse:
    return await service.create_training_job(payload)

async def get_job_status(
    job_id: str,
    service: JobService = Depends(get_job_service)
) -> JobStatusResponse:
    return await service.get_job_status(job_id)

async def list_jobs(
    page: int = 1,
    page_size: int = 10,
    service: JobService = Depends(get_job_service)
) -> JobListResponse:
    return await service.list_jobs(page=page, page_size=page_size)

async def cancel_job(
    job_id: str,
    service: JobService = Depends(get_job_service)
) -> JobCancelResponse:
    return await service.cancel_job(job_id)
