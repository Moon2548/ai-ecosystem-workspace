"""
ARQ Worker Settings — กำหนดค่า Worker สำหรับ Training Jobs

การใช้งาน:
  uv run arq core.worker_settings.WorkerSettings
"""

import os
from arq.connections import RedisSettings
from api.jobs.trainer import train_model

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379")

# แปลง Redis URL เป็น RedisSettings
_redis_clean = REDIS_URL.replace("redis://", "")
_host = _redis_clean.split(":")[0]
_port = int(_redis_clean.split(":")[1]) if ":" in _redis_clean else 6379


class WorkerSettings:
    """ARQ Worker configuration สำหรับ Training Jobs"""

    # ลงทะเบียน job functions ที่ Worker สามารถรันได้
    functions = [train_model]

    # เชื่อมต่อ Redis
    redis_settings = RedisSettings(host=_host, port=_port)

    # จำกัด 1 job ต่อครั้ง เพราะงานเทรนโมเดลใช้ทรัพยากรเยอะ (GPU)
    max_jobs = 1

    # Timeout 1 ชั่วโมงสำหรับงานเทรน
    job_timeout = 3600