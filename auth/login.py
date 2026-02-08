from fastapi import HTTPException, status

from auth.schemas import LoginRequest, TokenResponse
from auth.security import verify_password, create_access_token
from db.auth.auth_queries import get_user_by_email, update_last_login


async def login_user(payload: LoginRequest) -> TokenResponse:
    user = await get_user_by_email(payload.email)

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

    token = create_access_token({
        "sub": str(user["id"]),
        "role": user["role_id"],
    })

    return TokenResponse(access_token=token)
