from fastapi import HTTPException, status, Response
from datetime import timedelta

from auth.schemas import LoginRequest
from auth.security import verify_password, create_access_token
from db.auth.auth_queries import get_user_by_email, update_last_login


ACCESS_TOKEN_EXPIRE_MINUTES = 10


async def login_user(payload: LoginRequest, response: Response) -> None:
    user = await get_user_by_email(payload.login)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not verify_password(payload.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    await update_last_login(user["id"])

    access_token = create_access_token(
        data={
            "sub": str(user["id"]),
            "role": user["role_id"],
        },
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,       # In production True (HTTPS)
        samesite="lax",     # CSRF protection
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )