from sqlalchemy import Column, Integer, String
from db.base import Base

class TelegramAccount(Base):
    __tablename__ = "telegram_accounts"

    id = Column(Integer, primary_key=True, index=True)
    api_id = Column(Integer, nullable=False)
    api_hash = Column(String, nullable=False)
    session_string = Column(String, nullable=True)
