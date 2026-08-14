# Authentication Feature

## Overview
Authentication feature จัดการระบบยืนยันตัวตนของผู้ใช้ด้วย **JWT (JSON Web Token)**
รองรับการ login, register, และตรวจสอบผู้ใช้ปัจจุบัน

## Endpoints

| Method | Path | Description | Auth Required |
|--------|------|-------------|:------------:|
| POST | `/api/auth/login` | เข้าสู่ระบบด้วย email/password | ❌ |
| POST | `/api/auth/register` | สมัครสมาชิกใหม่ | ❌ |
| GET | `/api/auth/me` | ดูข้อมูลผู้ใช้ปัจจุบัน | ✅ |

## Authentication Flow

```
1. User ส่ง POST /api/auth/login { email, password }
2. Server ตรวจสอบ email → ดึง password_hash จาก PostgreSQL
3. ตรวจสอบ password ด้วย Argon2 hashing (pwdlib)
4. สร้าง JWT token → return { access_token, token_type: "bearer" }
5. User ใช้ token ใน Header: Authorization: Bearer <token>
```

## File Structure

| ไฟล์ | หน้าที่ |
|------|--------|
| `router.py` | Route definitions (POST /login, /register, GET /me) |
| `controller.py` | Request handling: login, register, get_me |
| `service.py` | AuthService: password verification, JWT generation/validation |
| `repository.py` | AuthRepository: CRUD operations กับตาราง users |
| `model.py` | User SQLAlchemy model (id, email, password_hash, created_at) |
| `schema.py` | LoginRequest, RegisterRequest, TokenResponse, UserResponse |

## Security
- **Password hashing**: Argon2 (via `pwdlib`) — ไม่เก็บ plain text password
- **JWT tokens**: HS256 algorithm, มี expiration time
- **Bearer auth**: ใช้ `HTTPBearer` dependency ใน protected routes

## Libraries ที่ใช้
| Library | หน้าที่ |
|---------|--------|
| `pwdlib[argon2]` | Password hashing ด้วย Argon2 |
| `PyJWT` | สร้างและตรวจสอบ JWT tokens |
| `email-validator` | Validate email format |
