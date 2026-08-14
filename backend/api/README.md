# API Module — Feature-Driven Modular Architecture

## Overview
API module จัดเก็บ feature modules ทั้งหมดของระบบ โดยใช้รูปแบบ
**Feature-Driven Modular Architecture** ที่จัดกลุ่มโค้ดตาม Feature/Domain

## โครงสร้าง Feature Module

แต่ละ feature มี folder ของตัวเองที่รวมทุก layer ไว้ด้วยกัน:

```
feature_name/
├── __init__.py       # Package marker + docstring
├── router.py         # API route definitions (ใช้ add_api_route pattern)
├── controller.py     # Request handling functions
├── service.py        # Business logic layer
├── schema.py         # Pydantic request/response models
├── model.py          # SQLAlchemy ORM models (ถ้ามี)
├── repository.py     # Data access layer (ถ้ามี)
└── README.md         # Feature documentation
```

## Features ในระบบ

| Feature | Path | หน้าที่ |
|---------|------|--------|
| **auth** | `/api/auth/` | Authentication: login, register, JWT token |
| **users** | `/api/users/` | User CRUD: ดู/แก้ไข/ลบข้อมูลผู้ใช้ |
| **inference** | `/api/inference/` | Inference Channel: รับ prediction request จาก End user |
| **management** | `/api/management/` | Management Channel: Admin จัดการระบบ |
| **jobs** | `/api/jobs/` | Job Worker: จัดการ Training Jobs ผ่าน Redis |

## Layer Responsibilities

| Layer | ไฟล์ | หน้าที่ |
|-------|------|--------|
| **Router** | `router.py` | กำหนด HTTP routes, method, status code, tags |
| **Controller** | `controller.py` | จัดการ request/response, dependency injection |
| **Service** | `service.py` | Business logic, การคำนวณ, การเชื่อมต่อ external services |
| **Schema** | `schema.py` | Pydantic models สำหรับ validate input/output |
| **Repository** | `repository.py` | CRUD operations กับ database |
| **Model** | `model.py` | SQLAlchemy table definitions |

## การเพิ่ม Feature ใหม่

1. สร้าง folder ใหม่ใน `api/` เช่น `api/new_feature/`
2. สร้างไฟล์ตาม pattern ด้านบน
3. Register router ใน `main.py`:
   ```python
   from api.new_feature.router import router as new_feature_router
   app.include_router(new_feature_router, prefix="/api")
   ```
