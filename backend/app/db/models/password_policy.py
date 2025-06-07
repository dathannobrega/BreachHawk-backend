from sqlalchemy import Column, Integer, Boolean
from db.base import Base

class PasswordPolicy(Base):
    __tablename__ = "password_policy"

    id = Column(Integer, primary_key=True, index=True)
    min_length = Column(Integer, nullable=False)
    require_uppercase = Column(Boolean, nullable=False)
    require_lowercase = Column(Boolean, nullable=False)
    require_numbers = Column(Boolean, nullable=False)
    require_symbols = Column(Boolean, nullable=False)
