from datetime import datetime
from pydantic import BaseModel, ConfigDict

class LoginHistoryRead(BaseModel):
    id: int
    user_id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
