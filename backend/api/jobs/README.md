# Job Worker

## Overview
Job Worker เป็น feature สำหรับจัดการ Training Jobs ในระบบ AI Ecosystem
ใช้ Redis Queue เป็น message broker ในการส่ง job ไปยัง Training Worker

## Architecture
- **Central API Server** → **Redis Queue** → **Job Worker** → **Training Worker**
- Job Worker รับคำสั่งสร้าง training job จาก API
- ส่ง job เข้า Redis queue
- Training Worker ดึง job จาก queue ไปประมวลผล
- ผลลัพธ์บันทึกลง **Annotated Database** (PostgreSQL)

## Endpoints
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/jobs/training` | สร้าง training job ใหม่ |
| GET | `/api/jobs/training` | แสดงรายการ jobs |
| GET | `/api/jobs/training/{job_id}` | ดูสถานะ job |
| DELETE | `/api/jobs/training/{job_id}` | ยกเลิก job |

## File Structure
- `router.py` — Route definitions
- `controller.py` — Request handling
- `service.py` — Business logic (Job dispatching via Redis)
- `schema.py` — Request/Response Pydantic models
