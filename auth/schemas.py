from pydantic import BaseModel, EmailStr, Field
from uuid import UUID

class LoginRequest(BaseModel):
    login: EmailStr
    password: str


class MeResponse(BaseModel):
    id: UUID
    login: str
    role: int


class FirstPasswordChangeRequest(BaseModel):
    new_password: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str