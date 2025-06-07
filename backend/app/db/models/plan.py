import enum
from sqlalchemy import Column, Integer, String, Enum
from db.base import Base

class PlanScope(str, enum.Enum):
    user = "user"
    company = "company"

class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    scope = Column(Enum(PlanScope), nullable=False)
    max_monitored_items = Column(Integer, nullable=False)
    max_users = Column(Integer, nullable=True)
