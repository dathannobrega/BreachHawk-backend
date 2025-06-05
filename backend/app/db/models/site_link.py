from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from db.base import Base

class SiteLink(Base):
    __tablename__ = "site_links"

    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False, index=True)
    url = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    site = relationship("Site", back_populates="links")

    __table_args__ = (
        UniqueConstraint("site_id", "url", name="uq_site_link"),
    )
