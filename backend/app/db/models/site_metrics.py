from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func
from db.base import Base

class SiteMetrics(Base):
    __tablename__ = "site_metrics"

    id             = Column(Integer, primary_key=True, index=True)
    site_id        = Column(Integer, ForeignKey("sites.id"), nullable=False, index=True)
    timestamp      = Column(DateTime(timezone=True), server_default=func.now())
    retries        = Column(Integer, nullable=False, default=0)   # quantas veces tentou
    permanent_fail = Column(Boolean, nullable=False, default=False)  # true se estourou retries
