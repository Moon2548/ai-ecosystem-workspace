from typing import List
from fastapi import Depends
from .schema import (
    DashboardResponse,
    ModelDeployRequest,
    ModelDeployResponse,
    ModelManagementInfo,
)
from .service import ManagementService

def get_management_service() -> ManagementService:
    return ManagementService()

async def get_dashboard(
    service: ManagementService = Depends(get_management_service)
) -> DashboardResponse:
    """Controller สำหรับแสดง Dashboard"""
    return await service.get_dashboard()

async def list_managed_models(
    service: ManagementService = Depends(get_management_service)
) -> List[ModelManagementInfo]:
    """Controller สำหรับแสดงรายการ Models"""
    return await service.list_managed_models()

async def deploy_model(
    payload: ModelDeployRequest,
    service: ManagementService = Depends(get_management_service)
) -> ModelDeployResponse:
    """Controller สำหรับ Deploy Model"""
    return await service.deploy_model(payload)

async def undeploy_model(
    model_name: str,
    service: ManagementService = Depends(get_management_service)
) -> dict:
    """Controller สำหรับ Undeploy Model"""
    return await service.undeploy_model(model_name)
