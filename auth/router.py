from fastapi import APIRouter
from auth.schemas import LoginRequest, TokenResponse
from auth.login import login_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    return await login_user(payload)
