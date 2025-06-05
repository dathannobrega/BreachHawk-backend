from enum import Enum
from pydantic import BaseModel, ConfigDict, field_validator

class AuthType(str, Enum):
    none  = "none"
    basic = "basic"
    form  = "form"

class CaptchaType(str, Enum):
    none    = "none"
    image   = "image"
    math    = "math"
    rotated = "rotated"

class SiteCreate(BaseModel):
    name: str
    links: list[str]
    auth_type: AuthType      = AuthType.none
    captcha_type: CaptchaType = CaptchaType.none
    scraper: str             = "generic"
    needs_js: bool           = False

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
    auth_type: AuthType | None = None
    captcha_type: CaptchaType | None = None
    scraper: str | None = None
    needs_js: bool | None = None

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
