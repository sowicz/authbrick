from pydantic import BaseModel, EmailStr
from uuid import UUID

class LoginRequest(BaseModel):
    login: EmailStr
    password: str


class MeResponse(BaseModel):
    id: UUID
    login: str
    role: int

    class Config:
        from_attributes = True  # jeśli kiedyś przejdziesz na ORM