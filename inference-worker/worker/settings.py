"""
ARQ Worker Settings — กำหนดค่า Inference Worker

การใช้งาน:
  python main.py
  หรือ: arq worker.settings.WorkerSettings
"""

import os
from arq.connections import RedisSettings
from worker.tasks import run_inference

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379")
_redis_clean = REDIS_URL.replace("redis://", "")
_host = _redis_clean.split(":")[0]
_port = int(_redis_clean.split(":")[1]) if ":" in _redis_clean else 6379


class WorkerSettings:
    """ARQ Worker configuration สำหรับ Inference Jobs"""

    # ลงทะเบียน job functions
    functions = [run_inference]

    # เชื่อมต่อ Redis
    redis_settings = RedisSettings(host=_host, port=_port)

    # Inference jobs สามารถรันพร้อมกันได้หลาย job
    # (ปรับตาม GPU VRAM ที่มี — ถ้าใช้ GPU จำกัดเป็น 1-2)
    max_jobs = 4

    # Timeout 5 นาทีต่อ job
    job_timeout = 300

    # Keep job results ใน ARQ 1 ชั่วโมง
    keep_result = 3600
