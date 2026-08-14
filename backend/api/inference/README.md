# Inference Channel

## Overview
Inference Channel เป็น feature ที่ให้บริการ inference/prediction สำหรับ End user
ทำหน้าที่รับข้อมูล input → ส่งไปประมวลผลผ่าน AI model → ส่งผลลัพธ์กลับ

## Architecture
- **End User** → **Central API Server** → **Inference Channel** → **Model**
- ใช้ **MinIO** เก็บ model files
- ใช้ **Redis** สำหรับ async inference queue (ในอนาคต)

## Endpoints
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/inference/predict` | ส่งข้อมูลเพื่อ predict |
| GET | `/api/inference/models` | แสดงรายการ models |
| GET | `/api/inference/models/{model_name}` | ดูรายละเอียด model |
| GET | `/api/inference/health` | ตรวจสอบสถานะ |

## File Structure
- `router.py` — Route definitions
- `controller.py` — Request handling
- `service.py` — Business logic (Inference pipeline)
- `schema.py` — Request/Response Pydantic models
