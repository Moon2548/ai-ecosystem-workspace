"""
Training Router — API endpoints สำหรับจัดการ Training Jobs ผ่าน ARQ

Endpoints:
  POST /training/queue      — สร้าง Training Job เข้าคิว ARQ
  GET  /training/queue/{id} — ตรวจสอบสถานะ Job
"""

import os
from fastapi import APIRouter, HTTPException
from arq import create_pool
from arq.connections import RedisSettings
from arq.jobs import Job, JobStatus

from .schema import QueueTrainRequest, QueueTrainResponse

router = APIRouter(prefix="/training", tags=["Training (Model Fine-tuning)"])

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379")
_redis_clean = REDIS_URL.replace("redis://", "")
_host = _redis_clean.split(":")[0]
_port = int(_redis_clean.split(":")[1]) if ":" in _redis_clean else 6379


async def get_arq_pool():
    """สร้าง ARQ Redis connection pool"""
    return await create_pool(RedisSettings(host=_host, port=_port))


@router.post(
    "/queue",
    response_model=QueueTrainResponse,
    status_code=201,
    summary="เพิ่มงาน Fine-tune Token Classification เข้าคิว ARQ",
    description="สร้าง training job และส่งเข้า ARQ queue โดยสามารถตั้งเวลาเริ่มเทรนล่วงหน้าได้",
)
async def enqueue_training(payload: QueueTrainRequest):
    pool = await get_arq_pool()
    try:
        # ใช้ ARQ _defer_until สำหรับตั้งเวลาเริ่มเทรนล่วงหน้า
        job = await pool.enqueue_job(
            "train_model",
            dataset_name=payload.dataset_name,
            model_name=payload.model_name,
            epochs=payload.epochs,
            batch_size=payload.batch_size,
            learning_rate=payload.learning_rate,
            _defer_until=payload.start_time,
        )
        return QueueTrainResponse(
            job_id=job.job_id,
            status="queued",
            message=f"Job queued successfully. Scheduled for: {payload.start_time or 'immediately'}",
        )
    finally:
        await pool.close()


@router.get(
    "/queue/{job_id}",
    summary="ตรวจสอบสถานะของงานเทรนผ่าน Job ID",
    description="ดึงสถานะปัจจุบัน, เวลาเริ่ม, และผลลัพธ์ (ถ้ามี) ของ Training Job",
)
async def get_training_status(job_id: str):
    pool = await get_arq_pool()
    try:
        job = Job(job_id, pool)
        status = await job.status()

        if status == JobStatus.not_found:
            raise HTTPException(status_code=404, detail="Job not found")

        info = await job.info()
        result = None
        if status == JobStatus.complete:
            try:
                result = await job.result(timeout=0.1)
            except Exception:
                result = None

        return {
            "job_id": job_id,
            "status": status.value,
            "enqueue_time": info.enqueue_time.isoformat() if info and info.enqueue_time else None,
            "start_time": info.start_time.isoformat() if info and info.start_time else None,
            "result": result,
        }
    finally:
        await pool.close()
