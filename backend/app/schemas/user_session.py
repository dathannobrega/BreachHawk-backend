from datetime import datetime
from pydantic import BaseModel, ConfigDict

class UserSessionRead(BaseModel):
    id: int
    user_id: int
    token: str
    created_at: datetime
    expires_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
