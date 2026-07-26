"""
Custom Logger Module
สำหรับการบันทึก logs ของ project ด้วย dual output (Terminal + File)

Features:
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Terminal output: INFO ขึ้นไป (สีสันสวยงาม)
- File output: DEBUG ขึ้นไป (เนื้อหา verbose มากกว่า)
- Automatic log rotation: 5MB per file, keep 3 files
- Structured format: [timestamp] [level] [module] - message
"""

import logging
import os
from logging.handlers import RotatingFileHandler

# Log configuration
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
LOG_FILE = os.path.join(LOG_DIR, "app.log")
LOG_FORMAT = "[%(asctime)s] [%(levelname)-8s] [%(name)s] - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
MAX_BYTES = 5 * 1024 * 1024  # 5MB
BACKUP_COUNT = 3  # Keep 3 backup files


def get_logger(name: str, level: int = logging.DEBUG) -> logging.Logger:
    """
    สร้าง logger ที่รองรับ dual output (terminal + file)
    
    Args:
        name: ชื่อ logger (ปกติใช้ __name__)
        level: Default log level (DEBUG = 10)
        
    Returns:
        logger object พร้อมใช้งาน
        
    Usage:
        logger = get_logger(__name__)
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
    """
    
    # สร้าง logs directory ถ้ายังไม่มี
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # สร้าง logger
    logger = logging.getLogger(name)
    
    # ตั้งค่า logger level
    logger.setLevel(level)
    
    # ถ้า logger มี handlers แล้ว ให้ return เลย (ป้องกัน duplicate)
    if logger.handlers:
        return logger
    
    # สร้าง formatter
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    
    # ===== HANDLER 1: CONSOLE (Terminal Output) =====
    # แสดง INFO ขึ้นไป ให้เห็นในหน้าจอ
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # ===== HANDLER 2: FILE (File Output) =====
    # เก็บ DEBUG ขึ้นไป (verbose มากกว่า terminal)
    # ใช้ RotatingFileHandler เพื่อหมุนไฟล์ที่ 5MB
    file_handler = RotatingFileHandler(
        filename=LOG_FILE,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger
