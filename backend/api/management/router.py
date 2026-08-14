from fastapi import APIRouter
from .controller import (
    get_dashboard,
    list_managed_models,
    deploy_model,
    undeploy_model
)
from .schema import (
    DashboardResponse,
    ModelDeployResponse,
    ModelManagementInfo
)

router = APIRouter(
    prefix='/management',
    tags=['Management Channel']
)

router.add_api_route(
    path="/dashboard",
    endpoint=get_dashboard,
    methods=["GET"],
    response_model=DashboardResponse,
    status_code=200,
    summary="แสดง Dashboard ข้อมูลระบบ",
    description="แสดงสถานะภาพรวมของระบบ AI Ecosystem สำหรับ Admin"
)

router.add_api_route(
    path="/models",
    endpoint=list_managed_models,
    methods=["GET"],
    response_model=list[ModelManagementInfo],
    status_code=200,
    summary="แสดงรายการ Models ที่จัดการได้"
)

router.add_api_route(
    path="/models/deploy",
    endpoint=deploy_model,
    methods=["POST"],
    response_model=ModelDeployResponse,
    status_code=201,
    summary="Deploy Model เข้าสู่ระบบ",
    description="Deploy model ที่เลือกเข้าสู่ระบบ inference สำหรับให้บริการ"
)

router.add_api_route(
    path="/models/{model_name}",
    endpoint=undeploy_model,
    methods=["DELETE"],
    status_code=200,
    summary="ถอด Model ออกจากระบบ"
)
