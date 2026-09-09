"""
Inference Tasks — ARQ job functions สำหรับ Inference Worker

Job: run_inference
  - รับ input_data และ model_name จาก FastAPI ผ่าน Redis
  - โหลด model จาก MLflow (cached)
  - รัน inference
  - เก็บผลลัพธ์ใน Redis key: inference:result:{job_id}
  - TTL ผล: 1 ชั่วโมง
"""

import json
import logging
import time
import uuid
from typing import Any

from worker.model_loader import load_model

logger = logging.getLogger(__name__)

# TTL ผลลัพธ์ใน Redis (วินาที)
RESULT_TTL_SECONDS = 3600  # 1 ชั่วโมง


async def run_inference(
    ctx,
    job_id: str,
    input_data: dict[str, Any],
    model_name: str = "bert-base-ner",
    model_stage: str = "Production",
    parameters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    ARQ Job Function — รัน NER inference บน input text

    Args:
        ctx: ARQ context (มี redis connection)
        job_id: UUID ของ job (ใช้เป็น Redis key สำหรับเก็บผล)
        input_data: dict ที่ต้องมี key "text" หรือ "texts" (list)
        model_name: ชื่อ model ใน MLflow Registry
        model_stage: stage ของ model
        parameters: optional parameters เพิ่มเติม

    Returns:
        dict ผลลัพธ์ inference พร้อม metadata
    """
    start_time = time.time()
    logger.info(f"[{job_id}] Starting inference job | model={model_name}:{model_stage}")

    redis = ctx["redis"]

    try:
        # ---- โหลด Model ----
        model = load_model(model_name=model_name, stage=model_stage)

        # ---- เตรียม Input ----
        texts = input_data.get("texts") or [input_data.get("text", "")]
        if not texts or not texts[0]:
            raise ValueError("input_data ต้องมี key 'text' (str) หรือ 'texts' (list[str])")

        logger.info(f"[{job_id}] Running inference on {len(texts)} sample(s)")

        # ---- รัน Inference ----
        raw_results = model(texts)

        # ---- จัดรูปแบบผลลัพธ์ ----
        # pipeline token-classification คืน list[list[dict]] หรือ list[dict]
        if isinstance(raw_results[0], dict):
            # single string input → pipeline คืน list[dict]
            formatted = [_format_entities(raw_results)]
        else:
            # list of strings → pipeline คืน list[list[dict]]
            formatted = [_format_entities(r) for r in raw_results]

        inference_time_ms = round((time.time() - start_time) * 1000, 2)

        result = {
            "job_id": job_id,
            "status": "completed",
            "model_name": model_name,
            "model_stage": model_stage,
            "inference_time_ms": inference_time_ms,
            "input_count": len(texts),
            "results": formatted,
        }

        # ---- เก็บผลใน Redis ----
        result_key = f"inference:result:{job_id}"
        await redis.setex(result_key, RESULT_TTL_SECONDS, json.dumps(result))
        logger.info(f"[{job_id}] Inference completed in {inference_time_ms}ms → saved to Redis")

        return result

    except Exception as e:
        error_result = {
            "job_id": job_id,
            "status": "failed",
            "error": str(e),
            "model_name": model_name,
        }
        # เก็บ error ใน Redis ด้วย
        result_key = f"inference:result:{job_id}"
        await redis.setex(result_key, RESULT_TTL_SECONDS, json.dumps(error_result))
        logger.error(f"[{job_id}] Inference failed: {e}")
        raise


def _format_entities(entities: list[dict]) -> list[dict]:
    """จัดรูปแบบ NER entities ให้อ่านง่าย"""
    return [
        {
            "text": e.get("word", e.get("entity", "")),
            "label": e.get("entity_group", e.get("entity", "")),
            "score": round(float(e.get("score", 0)), 4),
            "start": e.get("start"),
            "end": e.get("end"),
        }
        for e in entities
    ]
