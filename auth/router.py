from fastapi import APIRouter, Response, Request
from auth.schemas import LoginRequest
from auth.login import login_user
from auth.refresh import refresh_access_token


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(payload: LoginRequest, request: Request, response: Response):
    await login_user(payload, request, response)
    return {"status": "ok"}

router.post("/refresh")(refresh_access_token)