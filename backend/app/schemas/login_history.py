from datetime import datetime
from pydantic import BaseModel, ConfigDict

class LoginHistoryRead(BaseModel):
    id: int
    user_id: int
    timestamp: datetime
    device: str | None = None
    ip_address: str | None = None
    location: str | None = None
    success: bool

    model_config = ConfigDict(from_attributes=True)
