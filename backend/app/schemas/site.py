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
