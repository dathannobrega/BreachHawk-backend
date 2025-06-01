from pydantic import BaseModel, ConfigDict
from datetime import datetime

class SnapshotRead(BaseModel):
    id: int
    site_id: int
    taken_at: datetime
    html: str | None

    model_config = ConfigDict(from_attributes=True)
