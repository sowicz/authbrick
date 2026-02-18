from pydantic import BaseModel, EmailStr
from uuid import UUID

class SMTPCreateRequest(BaseModel):
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    from_email: EmailStr
    use_tls: bool = True
    is_active: bool = True


class SMTPUpdateRequest(BaseModel):
    id: UUID
    smtp_host: str | None = None
    smtp_port: int | None = None
    smtp_user: str | None = None
    smtp_password: str | None = None
    from_email: EmailStr | None = None
    use_tls: bool | None = None
    is_active: bool | None = None
