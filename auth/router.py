from fastapi import APIRouter, Response
from auth.schemas import LoginRequest
from auth.login import login_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", status_code=200)
async def login(payload: LoginRequest, response: Response):
    await login_user(payload, response)
    return {"status": "logged in"}
