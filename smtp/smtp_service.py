from fastapi import HTTPException, status, Depends
from auth.dependency import get_current_user

from db.smtp.smtp_queries import insert_smtp_config, get_active_smtp
from db.smtp.smtp_update_queries import update_smtp_config
from db.smtp.smtp_delete_queries import delete_smtp_config

from smtp.smtp_encrypt import encrypt_secret, decrypt_secret


def require_admin(user: dict = Depends(get_current_user)):
    if user["role_id"] not in (0, 1):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Privileges required",
        )
    return


async def create_smtp_config(payload, user :dict = Depends(get_current_user)):

    encrypted = encrypt_secret(payload.smtp_password)

    await insert_smtp_config(
        smtp_host=payload.smtp_host,
        smtp_port=payload.smtp_port,
        smtp_user=payload.smtp_user,
        smtp_password=encrypted,
        from_email=payload.from_email,
        use_tls=payload.use_tls,
        is_active=payload.is_active,
    )

    return {"status": "smtp_config_created"}


async def update_smtp(payload, user: dict = Depends(get_current_user)):
    data = payload.dict(exclude_none=True)
    config_id = data.pop("id", None)
    if not config_id:
        raise HTTPException(status_code=400, detail="ID is required in the request body")
    if "smtp_password" in data:
        data["smtp_password"] = encrypt_secret(data["smtp_password"])
    await update_smtp_config(config_id, **data)

    return {"status": "smtp_config_updated"}


async def remove_smtp(user:dict = Depends(get_current_user)):
    await delete_smtp_config()
    return {"status": "smtp_config_deleted"}


async def get_smtp(user:dict = Depends(get_current_user)):
    config = await get_active_smtp()
    if not config:
        raise HTTPException(
            status_code=404,
            detail="SMTP config not found",
        )

    return config
