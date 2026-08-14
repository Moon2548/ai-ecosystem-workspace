# Scripts

## Overview
รวม utility scripts สำหรับการจัดการและ maintenance ของระบบ

## Scripts ที่มี

### `export_openapi_to_csv.py` — แปลง OpenAPI JSON เป็น CSV

**Purpose**: สร้าง Snapshot API List จาก OpenAPI specification ของ FastAPI server

**วิธีที่เลือก**: เขียน Custom Python Script โดยใช้เฉพาะ Standard Library

**เหตุผลที่เลือกวิธีนี้**:
1. ใช้เฉพาะ Python standard library (`json`, `csv`, `urllib`) — ไม่ต้องติดตั้ง package เพิ่ม
2. ปรับแต่ง columns และ format ได้ตามต้องการ
3. รองรับทั้งการดึงจาก running server และอ่านจากไฟล์ `.json`
4. Output CSV เปิดได้ทันทีใน Excel, Google Sheets

**วิธีใช้**:
```bash
# ดึงจาก running server (ต้องรัน uvicorn ก่อน)
cd backend
uv run python scripts/export_openapi_to_csv.py

# ระบุ URL
uv run python scripts/export_openapi_to_csv.py --url http://localhost:8000/openapi.json

# ระบุ output file
uv run python scripts/export_openapi_to_csv.py --output my_api_list.csv

# ใช้ไฟล์ openapi.json ที่โหลดมาแล้ว
uv run python scripts/export_openapi_to_csv.py --file openapi.json
```

**CSV Columns**:
| Column | Description |
|--------|-------------|
| Method | HTTP Method (GET, POST, PUT, DELETE, etc.) |
| Path | API endpoint path |
| Summary | สรุปสั้นๆ ของ endpoint |
| Description | คำอธิบายเพิ่มเติม |
| Tags | Tags สำหรับจัดกลุ่ม |
| Operation ID | Function name ของ endpoint |
| Parameters | Path/Query parameters |
| Request Body | Schema ของ request body |
| Response Codes | HTTP response codes ที่ return |

**วิธีอื่นที่สามารถใช้ได้** (สำหรับอ้างอิง):
1. **`openapi-generator-cli`** — Command line tool ที่ generate ได้หลายรูปแบบ
2. **`swagger-cli`** — npm package สำหรับจัดการ Swagger/OpenAPI
3. **ใช้ `pandas` library** — `pd.json_normalize()` สำหรับแปลง JSON → DataFrame → CSV
