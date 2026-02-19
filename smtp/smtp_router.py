from fastapi import APIRouter, Depends

from auth.dependency import get_current_user
from .smtp_service import require_admin
from .smtp_service import (
    create_smtp_config,
    update_smtp,
    remove_smtp,
    get_smtp,
)
from .smtp_schemas import SMTPCreateRequest, SMTPUpdateRequest

router = APIRouter(prefix="/admin/smtp", tags=["SMTP"])


@router.post("/config")
async def create_config(payload: SMTPCreateRequest, user=Depends(get_current_user)):
    require_admin(user)
    return await create_smtp_config(payload)
 

@router.put("/config")
async def update_config(payload: SMTPUpdateRequest, user=Depends(get_current_user)):
    require_admin(user)
    return await update_smtp(payload)


@router.delete("/config")
async def delete_config(user=Depends(get_current_user)):
    require_admin(user)
    return await remove_smtp()


@router.get("/config")
async def read_config(user=Depends(get_current_user)):
    require_admin(user)
    return await get_smtp()
