# Inference Worker Dockerfile
# รองรับ GPU: เปลี่ยน base image เป็น nvidia/cuda ตาม comment ด้านล่าง
#
# CPU (default):
FROM python:3.12-slim
#
# GPU (uncomment บรรทัดด้านล่าง แล้ว comment บรรทัด CPU ด้านบน):
# FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

WORKDIR /app

# ติดตั้ง system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# ติดตั้ง uv (package manager)
RUN pip install uv

# คัดลอก dependency files
COPY pyproject.toml ./

# ติดตั้ง Python dependencies
RUN uv sync --no-dev

# คัดลอก source code
COPY . .

# ตั้งค่า PATH ให้เรียก python/libs จาก .venv
ENV PATH="/app/.venv/bin:$PATH"

# รัน ARQ worker
CMD ["python", "main.py"]
