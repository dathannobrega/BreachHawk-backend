from enum import Enum
from pydantic import BaseModel, ConfigDict
from typing import Optional

class PlanScope(str, Enum):
    user = "user"
    company = "company"

class PlanBase(BaseModel):
    name: str
    scope: PlanScope
    max_monitored_items: int
    max_users: Optional[int] = None
    max_searches: Optional[int] = None

class PlanCreate(PlanBase):
    pass

class PlanUpdate(BaseModel):
    name: Optional[str] = None
    scope: Optional[PlanScope] = None
    max_monitored_items: Optional[int] = None
    max_users: Optional[int] = None
    max_searches: Optional[int] = None

class PlanRead(PlanBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
