from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.auth.router import router as auth_router
from api.users.router import router as users_router
from core.config import settings
from db.database import create_database_schema


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Convenient for a new project; replace with Alembic migrations in production.
    await create_database_schema()
    yield


app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG_MODE, lifespan=lifespan, docs_url="/",)
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")



@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)