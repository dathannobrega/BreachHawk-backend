from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
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

class SiteType(str, enum.Enum):
    forum    = "forum"
    website  = "website"
    telegram = "telegram"
    discord  = "discord"
    paste    = "paste"

class Site(Base):
    __tablename__ = "sites"

    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String, nullable=False)
    url          = Column(String, unique=True, nullable=False)
    auth_type    = Column(Enum(AuthType), default=AuthType.none)
    captcha_type = Column(Enum(CaptchaType), default=CaptchaType.none)
    enabled      = Column(Boolean, default=True)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    scraper  = Column(String, default="generic", nullable=False)
    needs_js = Column(Boolean, default=False, nullable=False)
    type = Column(Enum(SiteType), default=SiteType.website, nullable=False)
    bypass_config = Column(String, nullable=True)
    credentials = Column(String, nullable=True)
    telegram_account_id = Column(Integer, ForeignKey("telegram_accounts.id"), nullable=True)

    telegram_account = relationship("TelegramAccount")

    links = relationship(
        "SiteLink",
        back_populates="site",
        cascade="all, delete-orphan",
    )


