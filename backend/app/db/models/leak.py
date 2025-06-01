from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from db.base import Base

class Leak(Base):
    __tablename__ = "leaks"

    id         = Column(Integer, primary_key=True, index=True)
    site_id    = Column(Integer, ForeignKey("sites.id"), nullable=False)
    company    = Column(String, nullable=False)
    country    = Column(String, nullable=True)
    found_at   = Column(DateTime(timezone=True), server_default=func.now())
    source_url = Column(String, nullable=False)
    views = Column(Integer, nullable=True)
    publication_date = Column(DateTime(timezone=True), nullable=True)
    amount_of_data = Column(String, nullable=True)
    information = Column(String, nullable=True)
    comment = Column(String, nullable=True)
    download_links = Column(String, nullable=True)  # JSON array
    rar_password = Column(String, nullable=True)

    __table_args__ = (UniqueConstraint("site_id", "company", "source_url", name="uq_leak"),)
