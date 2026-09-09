from fastapi import APIRouter
from . import controller
from .schema import (
    AsyncPredictResponse,
    InferenceHealthResponse,
    InferenceJobResult,
    ModelInfo,
    ModelListResponse,
)

router = APIRouter(
    prefix="/inference",
    tags=["Inference Channel"],
)

# POST /inference/predict — ส่ง request เข้า Redis queue, คืน job_id
router.add_api_route(
    path="/predict",
    endpoint=controller.predict,
    methods=["POST"],
    response_model=AsyncPredictResponse,
    status_code=202,
    summary="ส่งข้อมูลเพื่อ predict (Async)",
    description=(
        "รับ input text → enqueue inference job เข้า Redis → คืน job_id\n\n"
        "**Inference Worker** รับงาน → โหลด model จาก **MLflow** → รัน NER → เก็บผลใน Redis\n\n"
        "ดูผลลัพธ์ที่: `GET /api/inference/jobs/{job_id}`"
    ),
)

# GET /inference/jobs/{job_id} — ดูผลลัพธ์ inference job
router.add_api_route(
    path="/jobs/{job_id}",
    endpoint=controller.get_job_result,
    methods=["GET"],
    response_model=InferenceJobResult,
    status_code=200,
    summary="ดูผลลัพธ์ Inference Job",
    description=(
        "ดึงผลลัพธ์ inference ด้วย job_id ที่ได้จาก POST /predict\n\n"
        "**Status:**\n"
        "- `queued` — รอ Inference Worker รับงาน\n"
        "- `processing` — กำลังรัน inference\n"
        "- `completed` — เสร็จแล้ว ดูผลในฟิลด์ `results`\n"
        "- `failed` — เกิด error ดูใน `error`\n"
        "- `not_found` — job_id ไม่มีในระบบ (หรือหมด TTL)"
    ),
)

# GET /inference/models — รายการ models ที่พร้อมใช้งาน
router.add_api_route(
    path="/models",
    endpoint=controller.list_models,
    methods=["GET"],
    response_model=ModelListResponse,
    status_code=200,
    summary="แสดงรายการ Models ที่พร้อมใช้งาน",
)

# GET /inference/models/{model_name} — ข้อมูล model เฉพาะตัว
router.add_api_route(
    path="/models/{model_name}",
    endpoint=controller.get_model_info,
    methods=["GET"],
    response_model=ModelInfo,
    status_code=200,
    summary="ดูรายละเอียด Model",
)

# GET /inference/health — ตรวจสอบสถานะ
router.add_api_route(
    path="/health",
    endpoint=controller.check_health,
    methods=["GET"],
    response_model=InferenceHealthResponse,
    status_code=200,
    summary="ตรวจสอบสถานะ Inference Channel",
)
