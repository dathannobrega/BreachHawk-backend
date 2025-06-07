from enum import Enum
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional

class AuthType(str, Enum):
    none  = "none"
    basic = "basic"
    form  = "form"

class CaptchaType(str, Enum):
    none    = "none"
    image   = "image"
    math    = "math"
    rotated = "rotated"

class SiteType(str, Enum):
    forum = "forum"
    website = "website"
    telegram = "telegram"
    discord = "discord"
    paste = "paste"

class BypassConfig(BaseModel):
    useProxies: bool
    rotateUserAgent: bool
    captchaSolver: Optional[str] = None

class Credentials(BaseModel):
    username: str
    password: str
    token: Optional[str] = None

class SiteCreate(BaseModel):
    name: str
    links: list[str]
    type: SiteType = SiteType.website
    auth_type: AuthType      = AuthType.none
    captcha_type: CaptchaType = CaptchaType.none
    scraper: str             = "generic"
    needs_js: bool           = False
    bypassConfig: BypassConfig | None = None
    credentials: Credentials | None = None

    @field_validator("links", mode="before")
    @classmethod
    def cast_to_str_list(cls, v):
        return [str(item) for item in v]

    @field_validator("links")
    @classmethod
    def ensure_scheme(cls, values: list[str]) -> list[str]:
        normalized = []
        for url in values:
            if not url.startswith(("http://", "https://")):
                url = "http://" + url
            normalized.append(url.rstrip("/"))
        return normalized

class SiteRead(SiteCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class SiteUpdate(BaseModel):
    name: str | None = None
    links: list[str] | None = None
    type: SiteType | None = None
    auth_type: AuthType | None = None
    captcha_type: CaptchaType | None = None
    scraper: str | None = None
    needs_js: bool | None = None
    bypassConfig: BypassConfig | None = None
    credentials: Credentials | None = None

    @field_validator("links", mode="before")
    @classmethod
    def cast_to_str_list(cls, v):
        if v is None:
            return None
        return [str(item) for item in v]

    @field_validator("links")
    @classmethod
    def ensure_scheme(cls, values: list[str] | None):
        if values is None:
            return values
        normalized = []
        for url in values:
            if not url.startswith(("http://", "https://")):
                url = "http://" + url
            normalized.append(url.rstrip("/"))
        return normalized
