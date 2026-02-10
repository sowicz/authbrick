from fastapi import APIRouter, Response
from auth.schemas import LoginRequest
from auth.login import login_user
from auth.refresh import refresh_access_token


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", status_code=200)
async def login(payload: LoginRequest, response: Response):
    await login_user(payload, response)
    return {"status": "logged in"}


router.post("/refresh")(refresh_access_token)