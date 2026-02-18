from fastapi import APIRouter, Depends

from .smtp_service import (
    create_smtp_config,
    update_smtp,
    remove_smtp,
    get_smtp,
)
from .smtp_schemas import SMTPCreateRequest, SMTPUpdateRequest

router = APIRouter(prefix="/admin/smtp", tags=["SMTP"])


@router.post("/config")
async def create_config(payload: SMTPCreateRequest):
    return await create_smtp_config(payload)


@router.put("/config")
async def update_config(payload: SMTPUpdateRequest):
    return await update_smtp(payload)


@router.delete("/config")
async def delete_config():
    return await remove_smtp()


@router.get("/config")
async def read_config():
    return await get_smtp()
