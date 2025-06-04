from enum import Enum
from typing import Optional, Literal
from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict

class UserStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"

class PlatformUserCreate(BaseModel):
    username: Optional[str] = None
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Literal["user", "admin", "platform_admin"] = "user"
    status: UserStatus = UserStatus.active
    company: Optional[str] = None
    job_title: Optional[str] = None

class PlatformUserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[Literal["user", "admin", "platform_admin"]] = None
    status: Optional[UserStatus] = None
    company: Optional[str] = None
    job_title: Optional[str] = None

class PlatformUserRead(BaseModel):
    id: int
    username: Optional[str] = None
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str
    status: UserStatus
    company: Optional[str] = None
    job_title: Optional[str] = None
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
