from fastapi import HTTPException, status, Response, Request

from auth.security import (
    decode_token,
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
)
from db.auth.auth_queries import (
    get_user_by_id,
    get_valid_refresh_token,
    revoke_refresh_token,
    save_refresh_token,
)



async def refresh_access_token(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token",
        )

    payload = decode_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id = payload.get("sub")
    token_hash = hash_refresh_token(refresh_token)

    # Check if token is valid and not revoked
    db_token = await get_valid_refresh_token(token_hash)

    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token revoked or expired",
        )

    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Rotation - revoke old token
    await revoke_refresh_token(token_hash)

    # Create new refresh token and save to DB
    new_refresh_token = create_refresh_token({"sub": str(user_id)})
    new_refresh_hash = hash_refresh_token(new_refresh_token)

    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None

    await save_refresh_token(
        user_id=str(user_id),
        token_hash=new_refresh_hash,
        user_agent=user_agent,
        ip_address=ip_address,
    )

    # new access token
    new_access_token = create_access_token({
        "sub": str(user["id"]),
        "role": user["role_id"],
    })

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 10,
        path="/",
    )

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 30,
        path="/auth/refresh",
    )

    return {"status": "refreshed"}