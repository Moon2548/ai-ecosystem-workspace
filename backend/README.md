# Backend — AI Ecosystem Workspace

## Overview
Backend ของโปรเจกต์นี้ใช้ **FastAPI** เป็น **Central API Server** ตามแผนภาพ Architecture
โดยทำหน้าที่เป็นตัวกลางในการเชื่อมต่อส่วนประกอบต่างๆ ของระบบ AI Ecosystem

ใช้รูปแบบสถาปัตยกรรม **Feature-Driven Modular Architecture** ที่จัดกลุ่มโค้ดตาม Feature/Domain

## Directory Structure

```
backend/
├── main.py                     # FastAPI application entry point
├── pyproject.toml              # Python project dependencies
├── .env                        # Environment variables (ไม่ commit)
├── README.md                   # ไฟล์นี้
│
├── core/                       # Shared configuration & utilities
│   ├── config.py               # Pydantic BaseSettings configuration
│   ├── logger.py               # Custom dual-output logger
│   ├── worker_settings.py      # Background worker configuration
│   └── README.md
│
├── db/                         # Database connection modules
│   ├── database.py             # SQLAlchemy async engine & session
│   └── README.md
│
├── api/                        # Feature-Driven API modules
│   ├── README.md               # อธิบายโครงสร้าง Feature-Driven
│   │
│   ├── auth/                   # Authentication (login, register, JWT)
│   │   ├── router.py
│   │   ├── controller.py
│   │   ├── service.py
│   │   ├── repository.py
│   │   ├── model.py
│   │   ├── schema.py
│   │   └── README.md
│   │
│   ├── users/                  # User CRUD management
│   │   ├── router.py
│   │   ├── controller.py
│   │   ├── schema.py
│   │   └── README.md
│   │
│   ├── inference/              # Inference Channel (End user predictions)
│   │   ├── router.py
│   │   ├── controller.py
│   │   ├── service.py
│   │   ├── schema.py
│   │   └── README.md
│   │
│   ├── management/             # Management Channel (Admin operations)
│   │   ├── router.py
│   │   ├── controller.py
│   │   ├── service.py
│   │   ├── schema.py
│   │   └── README.md
│   │
│   └── jobs/                   # Job Worker (Training Jobs via Redis)
│       ├── router.py
│       ├── controller.py
│       ├── service.py
│       ├── schema.py
│       └── README.md
│
└── scripts/                    # Utility scripts
    ├── export_openapi_to_csv.py  # แปลง openapi.json → CSV
    └── README.md
```

## How to Run

```bash
# 1. เริ่ม infrastructure services
docker compose up -d

# 2. เข้า backend directory
cd backend

# 3. ติดตั้ง dependencies
uv sync

# 4. รัน development server
uv run uvicorn main:app --reload
```

## API Documentation

FastAPI มี built-in API documentation ที่สร้างจาก OpenAPI specification:

- **Swagger UI**: http://localhost:8000/ — Interactive API documentation
- **ReDoc**: http://localhost:8000/redoc — Alternative documentation view
- **OpenAPI JSON**: http://localhost:8000/openapi.json — Raw OpenAPI spec

### API Metadata
ใช้ `tags_metadata` และ `description` ใน FastAPI app สำหรับจัดกลุ่มและอธิบาย API
(อ้างอิง: https://fastapi.tiangolo.com/tutorial/metadata/)

### Export API List เป็น CSV
```bash
# ดึงจาก running server
uv run python scripts/export_openapi_to_csv.py

# หรือใช้ไฟล์ที่โหลดมาแล้ว
curl http://localhost:8000/openapi.json > openapi.json
uv run python scripts/export_openapi_to_csv.py --file openapi.json
```

## Dependencies

| Library | Version | หน้าที่ |
|---------|---------|--------|
| `fastapi` | ≥0.115.0 | Web framework สำหรับสร้าง API |
| `uvicorn[standard]` | ≥0.32.0 | ASGI server สำหรับรัน FastAPI |
| `sqlalchemy` | ≥2.0.0 | ORM สำหรับ PostgreSQL |
| `asyncpg` | ≥0.30.0 | Async PostgreSQL driver |
| `pydantic-settings` | ≥2.6.0 | Configuration management จาก .env |
| `redis` | ≥6.2.0 | Redis client สำหรับ Job queue |
| `minio` | ≥7.2.0 | MinIO client สำหรับ Object storage |
| `PyJWT` | ≥2.10.0 | JWT token creation & validation |
| `pwdlib[argon2]` | ≥0.2.1 | Password hashing ด้วย Argon2 |
| `email-validator` | ≥2.2.0 | Email format validation |
| `python-docx` | ≥1.1.0 | สร้างเอกสาร Word (.docx) |
