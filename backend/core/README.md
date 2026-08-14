# Core Module

## Overview
Core module เก็บ shared configuration และ utilities ที่ใช้ร่วมกันทั้งระบบ

## ไฟล์ในโมดูลนี้

### `config.py` — Application Configuration
- ใช้ **Pydantic `BaseSettings`** สำหรับ type-safe configuration
- โหลดค่าจากไฟล์ `.env` อัตโนมัติ
- ครอบคลุม settings สำหรับ: Database, Label Studio, MinIO, JWT Authentication

```python
from core.config import settings
# ใช้งาน
print(settings.database_url)
print(settings.minio_endpoint)
```

### `logger.py` — Custom Dual-Output Logger
- **Terminal output**: แสดง INFO level ขึ้นไป (สีสันอ่านง่าย)
- **File output**: บันทึก DEBUG level ขึ้นไป → `logs/app.log`
- ใช้ **RotatingFileHandler**: หมุนไฟล์ที่ 5MB, เก็บ 3 ไฟล์
- Format: `[timestamp] [level] [module] - message`

```python
from core.logger import get_logger
logger = get_logger(__name__)
logger.info("Server started")
logger.error("Connection failed")
```

### `worker_settings.py` — Background Worker Configuration
- กำหนดค่า background worker functions
- ใช้สำหรับ async job processing

## Libraries ที่เกี่ยวข้อง
| Library | หน้าที่ |
|---------|--------|
| `pydantic-settings` | Type-safe configuration from `.env` files |
| `logging` (built-in) | Python logging framework |
