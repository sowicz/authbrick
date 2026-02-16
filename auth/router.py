from fastapi import APIRouter, Response, Request, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from auth import change_password
from auth.schemas import FirstPasswordChangeRequest, LoginRequest, PasswordChangeRequest
from auth.login import login_user
from auth.refresh import refresh_access_token
from auth.dependency import get_current_user
from auth.schemas import MeResponse


router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


@router.post("/login")
async def login(payload: LoginRequest, request: Request, response: Response):
    await login_user(payload, request, response)
    return {"status": "ok"}



@router.post("/first-password-change")
async def first_password_change_endpoint(
    payload: FirstPasswordChangeRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    return await change_password.first_password_change(
        new_password=payload.new_password,
        credentials=credentials,
    )


@router.post("/password-change")
async def password_change_endpoint(
    payload: PasswordChangeRequest,
    user=Depends(get_current_user),
):
    return await change_password.password_change(
        current_password=payload.current_password,
        new_password=payload.new_password,
        user=user,
    )



@router.get("/me", response_model=MeResponse)
async def get_me(current_user=Depends(get_current_user)):
    return MeResponse(
        id=current_user["id"],
        login=current_user["email"],
        role=current_user["role_id"],
    )

router.post("/refresh")(refresh_access_token)