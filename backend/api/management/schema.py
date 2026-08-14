from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class SystemStatus(BaseModel):
    service_name: str
    status: str  # 'running'|'stopped'|'error'
    uptime_seconds: Optional[float] = None
    details: Optional[str] = None

class DashboardResponse(BaseModel):
    total_models: int
    total_jobs: int
    active_inferences: int
    system_services: List[SystemStatus]
    last_updated: str

class ModelDeployRequest(BaseModel):
    model_name: str
    version: str
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class ModelDeployResponse(BaseModel):
    model_name: str
    version: str
    status: str
    deployed_at: str
    message: str

class ModelManagementInfo(BaseModel):
    model_name: str
    version: str
    status: str
    deployed_at: Optional[str] = None
    size_mb: Optional[float] = None
    description: Optional[str] = None

    model_config = {"from_attributes": True}
