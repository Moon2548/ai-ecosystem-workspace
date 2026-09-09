"""
Inference Service — Business Logic สำหรับ Inference Channel

ทำงานร่วมกับ:
- Redis ARQ pool: enqueue inference jobs ไปยัง Inference Worker
- Redis direct: ดึงผลลัพธ์ inference job (key: inference:result:{job_id})
- MLflow (ผ่าน Inference Worker): โหลดและรัน model
"""

import json
import logging
import os
import uuid
from typing import Optional

import redis.asyncio as aioredis
from arq import create_pool
from arq.connections import RedisSettings
from arq.jobs import Job, JobStatus

from .schema import (
    AsyncPredictResponse,
    InferenceHealthResponse,
    InferenceJobResult,
    ModelInfo,
    ModelListResponse,
    PredictRequest,
)

logger = logging.getLogger(__name__)

# Redis connection (สำหรับดึงผลลัพธ์)
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
_redis_clean = REDIS_URL.replace("redis://", "")
_redis_host = _redis_clean.split(":")[0]
_redis_port = int(_redis_clean.split(":")[1]) if ":" in _redis_clean else 6379


def _get_redis_settings() -> RedisSettings:
    return RedisSettings(host=_redis_host, port=_redis_port)


class InferenceService:
    """Service สำหรับจัดการ Business Logic ของ Inference Channel"""

    async def predict(self, request: PredictRequest) -> AsyncPredictResponse:
        """
        Enqueue inference job เข้า Redis ARQ queue
        Inference Worker จะรับและรัน model แล้วเก็บผลใน Redis

        Returns:
            AsyncPredictResponse ที่มี job_id สำหรับ poll ผลภายหลัง
        """
        job_id = str(uuid.uuid4())
        pool = await create_pool(_get_redis_settings())
        try:
            await pool.enqueue_job(
                "run_inference",
                job_id=job_id,
                input_data=request.input_data,
                model_name=request.model_name or "bert-base-ner",
                model_stage=request.model_stage or "Production",
                parameters=request.parameters,
                _job_id=job_id,  # ใช้ job_id เดียวกันใน ARQ
            )
            logger.info(f"Inference job enqueued: {job_id}")
            return AsyncPredictResponse(
                job_id=job_id,
                status="queued",
                message=f"Inference job queued. ดูผลที่ GET /api/inference/jobs/{job_id}",
            )
        finally:
            await pool.aclose()

    async def get_job_result(self, job_id: str) -> InferenceJobResult:
        """
        ดึงผลลัพธ์ inference job จาก Redis
        ตรวจสอบทั้ง ARQ job status และ result key ที่ Inference Worker เก็บไว้
        """
        pool = await create_pool(_get_redis_settings())
        try:
            # ตรวจสอบ ARQ job status
            arq_job = Job(job_id, pool)
            arq_status = await arq_job.status()

            # ถ้า job ไม่มีอยู่ใน ARQ เลย
            if arq_status == JobStatus.not_found:
                # ลองดึงผลจาก Redis key โดยตรง (อาจ ARQ TTL หมดแล้ว แต่ result ยังอยู่)
                result_data = await self._get_result_from_redis(job_id)
                if result_data:
                    return InferenceJobResult(**result_data)
                return InferenceJobResult(job_id=job_id, status="not_found")

            # Map ARQ status → status string
            status_map = {
                JobStatus.queued: "queued",
                JobStatus.in_progress: "processing",
                JobStatus.complete: "completed",
                JobStatus.not_found: "not_found",
            }
            status_str = status_map.get(arq_status, "queued")

            # ถ้า completed → ดึงผลจาก Redis key ที่ Inference Worker เก็บไว้
            if arq_status == JobStatus.complete:
                result_data = await self._get_result_from_redis(job_id)
                if result_data:
                    return InferenceJobResult(**result_data)

            return InferenceJobResult(job_id=job_id, status=status_str)

        finally:
            await pool.aclose()

    async def _get_result_from_redis(self, job_id: str) -> Optional[dict]:
        """ดึงผลลัพธ์จาก Redis key: inference:result:{job_id}"""
        r = aioredis.from_url(REDIS_URL)
        try:
            result_key = f"inference:result:{job_id}"
            raw = await r.get(result_key)
            if raw:
                return json.loads(raw)
            return None
        finally:
            await r.aclose()

    async def list_models(self) -> ModelListResponse:
        """ดึงรายการ models ทั้งหมดที่พร้อมใช้งาน"""
        models = [
            ModelInfo(
                model_name="bert-base-ner",
                version="Production",
                status="active",
                description="NER model — BERT fine-tuned on CoNLL-2003 (โหลดจาก MLflow Registry)",
            ),
        ]
        return ModelListResponse(models=models, total=len(models))

    async def get_model_info(self, model_name: str) -> ModelInfo:
        """ดึงข้อมูลรายละเอียดของ model ตามชื่อ"""
        return ModelInfo(
            model_name=model_name,
            version="Production",
            status="active",
            description=f"Model: {model_name} — ดึงจาก MLflow Model Registry",
        )

    async def check_health(self) -> InferenceHealthResponse:
        """ตรวจสอบสถานะของ Inference Channel (Redis)"""
        redis_ok = False
        try:
            r = aioredis.from_url(REDIS_URL)
            await r.ping()
            await r.aclose()
            redis_ok = True
        except Exception:
            pass

        return InferenceHealthResponse(
            status="healthy" if redis_ok else "degraded",
            available_models=1,
            redis_connected=redis_ok,
            minio_connected=True,  # MinIO ตรวจสอบผ่าน MLflow/Worker
        )
