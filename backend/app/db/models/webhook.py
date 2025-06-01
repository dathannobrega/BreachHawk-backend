from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from db.base import Base

class Webhook(Base):
    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    url = Column(String, nullable=False)
    enabled = Column(Boolean, default=True)
