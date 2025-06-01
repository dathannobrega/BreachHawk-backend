from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime
from sqlalchemy.sql import func
from db.base import Base
import enum

class AuthType(str, enum.Enum):
    none = "none"
    basic = "basic"
    form  = "form"

class CaptchaType(str, enum.Enum):
    none      = "none"
    image     = "image"
    math      = "math"
    rotated   = "rotated"

class Site(Base):
    __tablename__ = "sites"

    id           = Column(Integer, primary_key=True, index=True)
    url          = Column(String, unique=True, nullable=False)
    auth_type    = Column(Enum(AuthType), default=AuthType.none)
    captcha_type = Column(Enum(CaptchaType), default=CaptchaType.none)
    enabled      = Column(Boolean, default=True)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    scraper  = Column(String, default="generic", nullable=False)
    needs_js = Column(Boolean, default=False, nullable=False)


