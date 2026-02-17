from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from auth.dependency import get_current_user
from auth.dependency import get_current_user
from auth.security import decode_token, hash_password, require_scope, verify_password
from db.auth.auth_login_queries import get_user_by_id
from db.auth.auth_update_queries import (
    is_first_login,
    update_user_password,
    disable_first_login,
    revoke_all_user_refresh_tokens,
)
from auth.password_policy import (
    validate_password_strength,
    validate_password_not_reused,
)

security = HTTPBearer()



async def first_password_change(
    new_password: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    payload = decode_token(token)

    if not require_scope(payload, "first_password_change"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token scope",
        )

    user_id = payload["sub"]

    if not await is_first_login(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="First login already completed",
        )
    
    user = await get_user_by_id(user_id)

    validate_password_strength(payload.new_password)
    validate_password_not_reused(payload.new_password, user["password"])

    hashed = hash_password(new_password)

    await update_user_password(user_id, hashed)
    await disable_first_login(user_id)
    await revoke_all_user_refresh_tokens(user_id)

    return {"status": "password_updated"}



async def password_change(
    current_password: str,
    new_password: str,
    user=Depends(get_current_user),
):
    if not verify_password(current_password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    
    validate_password_strength(new_password)
    validate_password_not_reused(new_password, user["password"])

    hashed = hash_password(new_password)

    await update_user_password(user["id"], hashed)

    return {"status": "password_updated"}