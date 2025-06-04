from sqlalchemy import Column, Integer, String, Enum, DateTime, Float
from sqlalchemy.sql import func
from db.base import Base
import enum

class PlanType(str, enum.Enum):
    trial = "trial"
    basic = "basic"
    professional = "professional"
    enterprise = "enterprise"

class CompanyStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    domain = Column(String, unique=True, nullable=False)
    plan = Column(Enum(PlanType), default=PlanType.trial, nullable=False)
    status = Column(Enum(CompanyStatus), default=CompanyStatus.active, nullable=False)
    contact_name = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    monthly_revenue = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
