from fastapi import APIRouter
from . import controller
from .schema import PredictResponse, ModelListResponse, ModelInfo, InferenceHealthResponse

router = APIRouter(
    prefix='/inference',
    tags=['Inference Channel']
)

router.add_api_route(
    path="/predict",
    endpoint=controller.predict,
    methods=["POST"],
    response_model=PredictResponse,
    status_code=200,
    summary="ส่งข้อมูลเพื่อ predict",
    description="รับข้อมูล input จาก End user ส่งไปประมวลผลผ่าน model ใน Inference Channel"
)

router.add_api_route(
    path="/models",
    endpoint=controller.list_models,
    methods=["GET"],
    response_model=ModelListResponse,
    status_code=200,
    summary="แสดงรายการ Models ที่พร้อมใช้งาน"
)

router.add_api_route(
    path="/models/{model_name}",
    endpoint=controller.get_model_info,
    methods=["GET"],
    response_model=ModelInfo,
    status_code=200,
    summary="ดูรายละเอียด Model"
)

router.add_api_route(
    path="/health",
    endpoint=controller.check_health,
    methods=["GET"],
    response_model=InferenceHealthResponse,
    status_code=200,
    summary="ตรวจสอบสถานะ Inference Channel"
)
