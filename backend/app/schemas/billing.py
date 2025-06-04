from pydantic import BaseModel
from typing import Optional

class Invoice(BaseModel):
    id: str
    customer: Optional[str] = None
    amount_due: int
    status: Optional[str] = None
    due_date: Optional[int] = None

class Payment(BaseModel):
    id: str
    amount: int
    status: Optional[str] = None
    created: int

class Subscription(BaseModel):
    id: str
    customer: Optional[str] = None
    status: Optional[str] = None
    current_period_end: Optional[int] = None
