from fastapi import Depends
from .schema import (
    AsyncPredictResponse,
    InferenceHealthResponse,
    InferenceJobResult,
    ModelInfo,
    ModelListResponse,
    PredictRequest,
)
from .service import InferenceService


def get_inference_service() -> InferenceService:
    """Dependency Provider สำหรับ InferenceService"""
    return InferenceService()


async def predict(
    payload: PredictRequest,
    service: InferenceService = Depends(get_inference_service),
) -> AsyncPredictResponse:
    """Controller รับข้อมูล predict แล้ว enqueue ไปยัง Inference Worker ผ่าน Redis"""
    return await service.predict(payload)


async def get_job_result(
    job_id: str,
    service: InferenceService = Depends(get_inference_service),
) -> InferenceJobResult:
    """Controller ดึงผลลัพธ์ inference job ด้วย job_id"""
    return await service.get_job_result(job_id)


async def list_models(
    service: InferenceService = Depends(get_inference_service),
) -> ModelListResponse:
    """Controller ดึงข้อมูล model ทั้งหมด"""
    return await service.list_models()


async def get_model_info(
    model_name: str,
    service: InferenceService = Depends(get_inference_service),
) -> ModelInfo:
    """Controller ดึงข้อมูล model เฉพาะชื่อ"""
    return await service.get_model_info(model_name)


async def check_health(
    service: InferenceService = Depends(get_inference_service),
) -> InferenceHealthResponse:
    """Controller ตรวจสอบสถานะ"""
    return await service.check_health()
