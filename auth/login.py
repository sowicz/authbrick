from fastapi import HTTPException, status, Response, Request

from auth.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
)
from db.auth.auth_queries import (
    get_user_by_email,
    update_last_login,
    save_refresh_token,
)


async def login_user(payload, request: Request, response: Response) -> None:
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


    token_hash = hash_refresh_token(refresh_token)

    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None

    await save_refresh_token(
        user_id=str(user["id"]),
        token_hash=token_hash,
        user_agent=user_agent,
        ip_address=ip_address,
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 10,
        path="/",
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 30,
        path="/auth/refresh",
    )