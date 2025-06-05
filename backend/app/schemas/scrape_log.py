from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ScrapeLogRead(BaseModel):
    id: int
    site_id: int
    url: str
    success: bool
    message: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
