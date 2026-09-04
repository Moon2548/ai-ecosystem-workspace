from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.auth.router import router as auth_router
from api.users.router import router as users_router
from api.inference.router import router as inference_router
from api.management.router import router as management_router
from api.jobs.router import router as jobs_router
from core.config import settings
from db.database import create_database_schema


# Tags metadata สำหรับ Swagger UI documentation
# อ้างอิง: https://fastapi.tiangolo.com/tutorial/metadata/
tags_metadata = [
    {
        "name": "system",
        "description": "System health check endpoints",
    },
    {
        "name": "auth",
        "description": "Authentication — ระบบยืนยันตัวตน (login, register, JWT token)",
    },
    {
        "name": "users",
        "description": "User Management — จัดการข้อมูลผู้ใช้ (CRUD operations)",
    },
    {
        "name": "Inference Channel",
        "description": "Inference Channel — รับ inference request จาก End user ส่งไปประมวลผลผ่าน AI model",
    },
    {
        "name": "Management Channel",
        "description": "Management Channel — สำหรับ Admin จัดการระบบ ดู Dashboard และ Deploy/Undeploy models",
    },
    {
        "name": "Training (Model Fine-tuning)",
        "description": "Training — จัดการ Training Jobs ผ่าน ARQ (Async Redis Queue) ไปยัง Trainer Worker",
    },
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Convenient for a new project; replace with Alembic migrations in production.
    await create_database_schema()
    yield


app = FastAPI(
    title="AI Ecosystem API",
    description="""
## AI Ecosystem Workspace — Central API Server

ระบบ AI ครบวงจรที่รวมการจัดการ Machine Learning Pipeline

### ส่วนประกอบหลัก:
- **Inference Channel**: รับ prediction request จาก End user
- **Management Channel**: Admin จัดการระบบ, Deploy models
- **Job Worker**: สร้างและติดตาม Training Jobs ผ่าน Redis queue
- **Authentication**: ระบบยืนยันตัวตนด้วย JWT

### สถาปัตยกรรม: Feature-Driven Modular Architecture
จัดกลุ่มโค้ดตาม Feature/Domain — แต่ละ feature มี router, controller, service, schema
    """,
    version="0.1.0",
    contact={
        "name": "AI Ecosystem Team",
    },
    license_info={
        "name": "MIT",
    },
    openapi_tags=tags_metadata,
    debug=settings.DEBUG_MODE,
    lifespan=lifespan,
    docs_url="/",
)

# Register all feature routers
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(inference_router, prefix="/api")
app.include_router(management_router, prefix="/api")
app.include_router(jobs_router, prefix="/api")


@app.get("/health", tags=["system"], summary="System Health Check",
         description="ตรวจสอบสถานะของ Central API Server")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)