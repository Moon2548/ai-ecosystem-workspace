"""
Inference Worker — Entry Point

รัน ARQ worker ที่รับ inference jobs จาก Redis queue
แล้วส่งผลกลับผ่าน Redis key

การใช้งาน:
  python main.py
"""

import asyncio
import logging
import os

from arq import run_worker
from worker.settings import WorkerSettings

# ตั้งค่า logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 60)
    logger.info("Inference Worker starting...")
    logger.info(f"  Redis     : {os.environ.get('REDIS_URL', 'redis://localhost:6379')}")
    logger.info(f"  MLflow    : {os.environ.get('MLFLOW_TRACKING_URI', 'http://localhost:5000')}")
    logger.info(f"  Model     : {os.environ.get('MODEL_NAME', 'bert-base-ner')}")
    logger.info(f"  Stage     : {os.environ.get('MODEL_STAGE', 'Production')}")
    logger.info("=" * 60)

    run_worker(WorkerSettings)


if __name__ == "__main__":
    main()
