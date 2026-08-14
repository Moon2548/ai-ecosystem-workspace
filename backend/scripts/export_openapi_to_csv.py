"""
Export OpenAPI Specification to CSV

สคริปต์สำหรับดึง openapi.json จาก FastAPI server แล้วแปลงเป็น CSV
เพื่อใช้เป็น Snapshot API List ของระบบ

วิธีใช้:
    # ดึงจาก running server (default: http://localhost:8000)
    python scripts/export_openapi_to_csv.py

    # ระบุ URL
    python scripts/export_openapi_to_csv.py --url http://localhost:8000/openapi.json

    # ระบุ output file
    python scripts/export_openapi_to_csv.py --output api_list.csv

    # ใช้ไฟล์ openapi.json ที่ดาวน์โหลดมาแล้ว
    python scripts/export_openapi_to_csv.py --file openapi.json

เหตุผลที่เลือกวิธีนี้:
    - ใช้เฉพาะ Python standard library (json, csv, urllib) ไม่ต้องติดตั้งเพิ่ม
    - รองรับทั้งการดึงจาก server และอ่านจากไฟล์
    - Output CSV สามารถเปิดใน Excel, Google Sheets ได้ทันที
    - เป็น custom python script ที่ปรับแต่ง columns ได้ตามต้องการ
"""

import argparse
import csv
import json
import sys
import urllib.request
from pathlib import Path


def fetch_openapi_json(url: str) -> dict:
    """ดึง openapi.json จาก URL"""
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as e:
        print(f"Error: ไม่สามารถเชื่อมต่อ {url}")
        print(f"       กรุณาตรวจสอบว่า server กำลังทำงานอยู่")
        print(f"       Detail: {e}")
        sys.exit(1)


def load_openapi_file(filepath: str) -> dict:
    """โหลด openapi.json จากไฟล์"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: ไม่พบไฟล์ {filepath}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: ไฟล์ {filepath} ไม่ใช่ JSON ที่ถูกต้อง")
        print(f"       Detail: {e}")
        sys.exit(1)


def extract_parameters(parameters: list[dict]) -> str:
    """แปลง parameters list เป็น string"""
    if not parameters:
        return ""
    parts = []
    for param in parameters:
        name = param.get("name", "")
        location = param.get("in", "")
        required = param.get("required", False)
        param_type = param.get("schema", {}).get("type", "")
        marker = "*" if required else ""
        parts.append(f"{name}{marker} ({location}, {param_type})")
    return "; ".join(parts)


def extract_request_body(request_body: dict | None) -> str:
    """แปลง request body schema เป็น string"""
    if not request_body:
        return ""
    content = request_body.get("content", {})
    for content_type, schema_info in content.items():
        ref = schema_info.get("schema", {}).get("$ref", "")
        if ref:
            return ref.split("/")[-1]
    return "object"


def extract_response_codes(responses: dict) -> str:
    """แปลง response codes เป็น string"""
    if not responses:
        return ""
    return ", ".join(sorted(responses.keys()))


def openapi_to_csv(openapi_data: dict, output_file: str) -> list[dict]:
    """แปลง OpenAPI spec เป็น CSV"""
    rows = []
    paths = openapi_data.get("paths", {})

    for path, methods in paths.items():
        for method, details in methods.items():
            if method in ("get", "post", "put", "patch", "delete", "head", "options"):
                row = {
                    "Method": method.upper(),
                    "Path": path,
                    "Summary": details.get("summary", ""),
                    "Description": details.get("description", "").replace("\n", " ").strip(),
                    "Tags": ", ".join(details.get("tags", [])),
                    "Operation ID": details.get("operationId", ""),
                    "Parameters": extract_parameters(details.get("parameters", [])),
                    "Request Body": extract_request_body(details.get("requestBody")),
                    "Response Codes": extract_response_codes(details.get("responses", {})),
                }
                rows.append(row)

    # Sort by path then method
    rows.sort(key=lambda x: (x["Path"], x["Method"]))

    # Write CSV
    if rows:
        fieldnames = list(rows[0].keys())
        with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"✅ Export สำเร็จ: {output_file}")
        print(f"   จำนวน endpoints: {len(rows)}")
    else:
        print("⚠️ ไม่พบ endpoints ใน OpenAPI spec")

    return rows


def print_summary(rows: list[dict], openapi_data: dict) -> None:
    """แสดงสรุปข้อมูล API"""
    info = openapi_data.get("info", {})
    print("\n" + "=" * 60)
    print(f"API: {info.get('title', 'N/A')}")
    print(f"Version: {info.get('version', 'N/A')}")
    print(f"Total Endpoints: {len(rows)}")
    print("=" * 60)

    # Count by method
    method_counts = {}
    for row in rows:
        m = row["Method"]
        method_counts[m] = method_counts.get(m, 0) + 1

    print("\nEndpoints by Method:")
    for method, count in sorted(method_counts.items()):
        print(f"  {method}: {count}")

    # Count by tag
    tag_counts = {}
    for row in rows:
        for tag in row["Tags"].split(", "):
            if tag:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

    if tag_counts:
        print("\nEndpoints by Tag:")
        for tag, count in sorted(tag_counts.items()):
            print(f"  {tag}: {count}")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Export OpenAPI specification to CSV (Snapshot API List)"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000/openapi.json",
        help="URL ของ openapi.json (default: http://localhost:8000/openapi.json)",
    )
    parser.add_argument(
        "--file",
        help="Path ของไฟล์ openapi.json (ใช้แทน --url ถ้ามีไฟล์อยู่แล้ว)",
    )
    parser.add_argument(
        "--output",
        default="api_snapshot.csv",
        help="ชื่อไฟล์ CSV output (default: api_snapshot.csv)",
    )
    args = parser.parse_args()

    # Load OpenAPI data
    if args.file:
        print(f"📂 โหลดจากไฟล์: {args.file}")
        openapi_data = load_openapi_file(args.file)
    else:
        print(f"🌐 ดึงจาก: {args.url}")
        openapi_data = fetch_openapi_json(args.url)

    # Export to CSV
    rows = openapi_to_csv(openapi_data, args.output)

    # Print summary
    if rows:
        print_summary(rows, openapi_data)


if __name__ == "__main__":
    main()
