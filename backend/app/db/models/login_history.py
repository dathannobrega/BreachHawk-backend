from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Boolean
from sqlalchemy.sql import func
from db.base import Base

class LoginHistory(Base):
    __tablename__ = "login_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    device = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    location = Column(String, nullable=True)
    success = Column(Boolean, default=True)
