# schemas/leak.py

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

class LeakRead(BaseModel):
    id: int
    company: str
    country: Optional[str]
    found_at: datetime
    source_url: str

    views: Optional[int]
    publication_date: Optional[datetime]
    amount_of_data: Optional[str]
    information: Optional[str]
    comment: Optional[str]
    download_links: Optional[List[str]]
    rar_password: Optional[str]

    model_config = ConfigDict(from_attributes=True)
