# Database Module

## Overview
Database module จัดการการเชื่อมต่อฐานข้อมูลทั้งหมดของระบบ

## ไฟล์ในโมดูลนี้

### `database.py` — SQLAlchemy Async Engine & Session

#### Components:
- **`Base`** — SQLAlchemy `DeclarativeBase` สำหรับสร้าง ORM models
- **`engine`** — Async database engine เชื่อมต่อ PostgreSQL ผ่าน `asyncpg`
- **`SessionLocal`** — Async session factory สำหรับสร้าง database sessions
- **`get_db_session()`** — Dependency function สำหรับ FastAPI injection
- **`create_database_schema()`** — สร้าง tables อัตโนมัติตอน startup (ใช้ใน lifespan)

#### การใช้งาน:
```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db_session

async def my_endpoint(session: AsyncSession = Depends(get_db_session)):
    # ใช้ session สำหรับ query
    result = await session.execute(...)
```

## Database ที่เชื่อมต่อ

### PostgreSQL
- **Purpose**: ฐานข้อมูลหลักของระบบ + Label Studio backend
- **Driver**: `asyncpg` (async PostgreSQL driver)
- **ORM**: SQLAlchemy 2.0+ (async mode)
- **Connection**: กำหนดผ่าน `DATABASE_URL` ใน `.env`
- **Port**: `5433` (mapped from container's `5432`)

## Libraries ที่เกี่ยวข้อง
| Library | หน้าที่ |
|---------|--------|
| `sqlalchemy[asyncio]` | ORM + async database engine |
| `asyncpg` | Async PostgreSQL driver |
