from fastapi import APIRouter, Response, Request, Depends
from auth.schemas import LoginRequest
from auth.login import login_user
from auth.refresh import refresh_access_token
from auth.dependency import get_current_user
from auth.schemas import MeResponse


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(payload: LoginRequest, request: Request, response: Response):
    await login_user(payload, request, response)
    return {"status": "ok"}


@router.get("/me", response_model=MeResponse)
async def get_me(current_user=Depends(get_current_user)):
    return MeResponse(
        id=current_user["id"],
        login=current_user["email"],
        role=current_user["role_id"],
    )

router.post("/refresh")(refresh_access_token)