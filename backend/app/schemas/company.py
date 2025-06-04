from enum import Enum
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

class PlanType(str, Enum):
    trial = "trial"
    basic = "basic"
    professional = "professional"
    enterprise = "enterprise"

class CompanyStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"

class CompanyBase(BaseModel):
    name: str
    domain: str
    contact_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    plan: PlanType = PlanType.trial
    status: CompanyStatus = CompanyStatus.active

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    plan: Optional[PlanType] = None
    status: Optional[CompanyStatus] = None

class CompanyRead(CompanyBase):
    id: int
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
