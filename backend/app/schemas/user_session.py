from datetime import datetime
from pydantic import BaseModel, ConfigDict

class UserSessionRead(BaseModel):
    id: int
    user_id: int
    token: str
    device: str | None = None
    ip_address: str | None = None
    location: str | None = None
    created_at: datetime
    expires_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
