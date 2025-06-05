from sqlalchemy import Column, Integer, String
from db.base import Base

class SMTPConfig(Base):
    __tablename__ = "smtp_config"

    id = Column(Integer, primary_key=True, index=True)
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    from_email = Column(String, nullable=False)
