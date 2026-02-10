from fastapi import HTTPException, status, Response

from auth.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
)
from db.auth.auth_queries import get_user_by_email, update_last_login


ACCESS_TOKEN_EXPIRE_MINUTES = 10


async def login_user(payload, response: Response) -> None:
    user = await get_user_by_email(payload.login)

    if not user or not verify_password(payload.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    await update_last_login(user["id"])

    access_token = create_access_token({
        "sub": str(user["id"]),
        "role": user["role_id"],
    })

    refresh_token = create_refresh_token({
        "sub": str(user["id"]),
    })

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,       # True in production
        samesite="lax",
        max_age=60 * 10,
        path="/",
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,      # True in production
        samesite="lax",
        max_age=60 * 60 * 24 * 30,
        path="/auth/refresh",
    )