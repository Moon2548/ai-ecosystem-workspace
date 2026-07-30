from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from api.auth.repository import AuthRepository
from core.config import settings

password_hash = PasswordHash.recommended()


class InvalidCredentialsError(Exception):
    pass


class AuthService:
    def __init__(self, repository: AuthRepository) -> None:
        self.repository = repository

    async def login(self, email: str, password: str) -> str:
        user = await self.repository.get_user_by_email(email)
        if user is None or not password_hash.verify(password, user.password_hash):
            raise InvalidCredentialsError

        expires_at = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return jwt.encode(
            {"sub": str(user.id), "email": user.email, "exp": expires_at},
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
