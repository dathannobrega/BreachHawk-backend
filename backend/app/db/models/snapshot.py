# db/models/snapshot.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey, LargeBinary, Text
from sqlalchemy.sql import func
from db.base import Base

class ScrapeSnapshot(Base):
    __tablename__ = "scrape_snapshots"

    id          = Column(Integer, primary_key=True)
    site_id     = Column(Integer, ForeignKey("sites.id"), nullable=False)
    taken_at    = Column(DateTime(timezone=True), server_default=func.now())
    screenshot  = Column(LargeBinary, nullable=False)      # PNG bytes
    html        = Column(Text, nullable=True)              # opcional
