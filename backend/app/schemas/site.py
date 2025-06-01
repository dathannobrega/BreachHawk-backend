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
    url: str
    auth_type: AuthType     = AuthType.none
    captcha_type: CaptchaType = CaptchaType.none
    scraper: str            = "generic"
    needs_js: bool          = False

    @field_validator("url", mode="before")
    @classmethod
    def cast_to_str(cls, v):
        return str(v)

    @field_validator("url")
    @classmethod
    def ensure_scheme(cls, v: str) -> str:
        # adiciona http:// se o usuário esquecer
        if not v.startswith(("http://", "https://")):
            v = "http://" + v
        return v.rstrip("/")

class SiteRead(SiteCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
