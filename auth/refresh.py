from fastapi import HTTPException, status, Response, Request

from auth.security import decode_token, create_access_token
from db.auth.auth_queries import get_user_by_id


# ============================
# ENDPOINT NIE SPRAWDZANY - DO WERYFIKACJI
# ============================

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
    user = await get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error unauthorized",
        )

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

    return {"status": "refreshed"}
