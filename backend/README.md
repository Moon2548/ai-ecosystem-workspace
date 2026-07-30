## Authentication API

Start PostgreSQL from the repository root, then create `backend/.env` from the example below and run the API.

```env
DATABASE_URL=postgresql+asyncpg://myuser:mypassword@localhost:5433/labelstudio
JWT_SECRET_KEY=replace-with-a-long-random-secret
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

```powershell
docker compose up -d postgres
cd backend
uv sync
uv run uvicorn main:app --reload
```

`POST /api/v1/auth/login`

```json
{ "email": "user@example.com", "password": "your-password" }
```

The endpoint returns a bearer JWT. Users must already be present in PostgreSQL with an Argon2 hash in `users.password_hash`; passwords are deliberately never stored in plain text. The feature is structured as `api/auth/{router,controller,service,repository,schema,model}.py`.
