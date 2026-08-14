# Management Channel

## Overview
Management Channel เป็น feature สำหรับ Admin ในการจัดการระบบ AI Ecosystem
รวมถึงการดู Dashboard, จัดการ Models, ดูสถานะ Services

## Architecture
- **Admin** → **Central API Server** → **Management Channel**
- เชื่อมต่อ **PostgreSQL** สำหรับข้อมูลระบบ
- เชื่อมต่อ **MinIO** สำหรับจัดการ model files

## Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/management/dashboard` | แสดง Dashboard ภาพรวม |
| GET | `/api/management/models` | แสดงรายการ models |
| POST | `/api/management/models/deploy` | Deploy model |
| DELETE | `/api/management/models/{model_name}` | ถอด model |

## File Structure
- `router.py` — Route definitions
- `controller.py` — Request handling
- `service.py` — Business logic (Admin operations)
- `schema.py` — Request/Response Pydantic models
