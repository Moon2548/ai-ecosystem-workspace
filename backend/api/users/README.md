# Users Feature

## Overview
Users feature จัดการข้อมูลผู้ใช้ในระบบ รองรับ CRUD operations
ทุก endpoint ต้องมี JWT authentication

## Endpoints

| Method | Path | Description | Auth Required |
|--------|------|-------------|:------------:|
| GET | `/api/users` | แสดงรายการผู้ใช้ทั้งหมด | ✅ |
| GET | `/api/users/{user_id}` | ดูข้อมูลผู้ใช้เฉพาะราย | ✅ |
| PATCH | `/api/users/{user_id}` | แก้ไขข้อมูลผู้ใช้ | ✅ (เจ้าของเท่านั้น) |
| DELETE | `/api/users/{user_id}` | ลบผู้ใช้ | ✅ (เจ้าของเท่านั้น) |

## File Structure

| ไฟล์ | หน้าที่ |
|------|--------|
| `router.py` | Route definitions (GET, PATCH, DELETE /users) |
| `controller.py` | Request handling + permission checks |
| `schema.py` | UpdateUserRequest (email, password — ต้องมีอย่างน้อย 1 field) |

## Permission Rules
- **GET /users**: ผู้ใช้ที่ login แล้วดูได้ทุกคน
- **PATCH /users/{id}**: แก้ไขได้เฉพาะข้อมูลของตัวเอง (`current_user.id == user_id`)
- **DELETE /users/{id}**: ลบได้เฉพาะตัวเอง

## Dependencies
- ใช้ `AuthRepository` จาก `api.auth` สำหรับ database operations
- ใช้ `get_current_user` จาก `api.auth.service` สำหรับ JWT validation
