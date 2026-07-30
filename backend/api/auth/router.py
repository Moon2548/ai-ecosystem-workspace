from fastapi import APIRouter, status

from api.auth.controller import login
from api.auth.schema import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])
router.add_api_route("/login", login, methods=["POST"], response_model=TokenResponse, status_code=status.HTTP_200_OK)
