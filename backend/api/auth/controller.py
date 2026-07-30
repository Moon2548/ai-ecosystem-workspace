from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.repository import AuthRepository
from api.auth.schema import LoginRequest, TokenResponse
from api.auth.service import AuthService, InvalidCredentialsError
from db.database import get_db_session


async def login(payload: LoginRequest, session: AsyncSession = Depends(get_db_session)) -> TokenResponse:
    service = AuthService(AuthRepository(session))
    try:
        token = await service.login(payload.email, payload.password)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    return TokenResponse(access_token=token)
