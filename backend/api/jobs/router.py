from fastapi import APIRouter
from . import controller

router = APIRouter(prefix="/jobs", tags=["Job Worker"])

router.add_api_route(
    "/training",
    controller.create_training_job,
    methods=["POST"],
    status_code=201,
    summary="สร้าง Training Job ใหม่",
    description="สร้าง training job และส่งเข้า Redis queue เพื่อให้ Training Worker ประมวลผล"
)

router.add_api_route(
    "/training",
    controller.list_jobs,
    methods=["GET"],
    status_code=200,
    summary="แสดงรายการ Training Jobs ทั้งหมด"
)

router.add_api_route(
    "/training/{job_id}",
    controller.get_job_status,
    methods=["GET"],
    status_code=200,
    summary="ดูสถานะ Training Job",
    description="ตรวจสอบสถานะและ progress ของ training job ที่กำลังทำงาน"
)

router.add_api_route(
    "/training/{job_id}",
    controller.cancel_job,
    methods=["DELETE"],
    status_code=200,
    summary="ยกเลิก Training Job"
)
