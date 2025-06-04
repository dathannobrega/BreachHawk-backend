from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, EmailStr, ConfigDict


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class AuthResponse(Token):
    user: "UserOut"

class TokenData(BaseModel):
    username: str | None = None

class UserLogin(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    password: str

class UserCreate(BaseModel):
    username: str | None = None
    email: EmailStr
    password: str
    first_name: str | None = None
    last_name: str | None = None
    company: str | None = None
    job_title: str | None = None

class UserOut(BaseModel):
    id: int
    username: str | None = None
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    role: Literal["admin", "user", "platform_admin"]
    company: str | None = None
    job_title: str | None = None
    profile_image: str | None = None
    organization: str | None = None
    contact: str | None = None
    is_subscribed: bool
    model_config = ConfigDict(from_attributes=True)

class PasswordChange(BaseModel):
    old_password: str
    new_password: str


class UserUpdate(BaseModel):
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    company: str | None = None
    job_title: str | None = None
    profile_image: str | None = None
    organization: str | None = None
    contact: str | None = None
    is_subscribed: bool | None = None
