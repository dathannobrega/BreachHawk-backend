from pydantic import BaseModel, EmailStr, ConfigDict

class SMTPConfigRead(BaseModel):
    id: int | None = None
    host: str
    port: int
    username: str
    from_email: EmailStr

    model_config = ConfigDict(from_attributes=True)

class SMTPConfigUpdate(BaseModel):
    host: str
    port: int
    username: str
    password: str
    from_email: EmailStr

class TestEmailRequest(BaseModel):
    to_email: EmailStr
