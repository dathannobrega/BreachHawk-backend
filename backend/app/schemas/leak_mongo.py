# schemas/leak_mongo.py

from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional, List

class LeakDoc(BaseModel):
    site_id: int
    company: str
    source_url: HttpUrl
    found_at: datetime = Field(default_factory=datetime.utcnow)

    # agora com default=None
    country: Optional[str]            = None
    views: Optional[int]              = None
    publication_date: Optional[datetime] = None
    amount_of_data: Optional[str]     = None
    information: Optional[str]        = None
    comment: Optional[str]            = None
    download_links: Optional[List[HttpUrl]] = None
    rar_password: Optional[str]       = None

    class Config:
        json_schema_extra = {
            "example": {
                "site_id": 1,
                "company": "Acme Corp",
                "source_url": "http://exemplo.onion/leak/123",
                "found_at": "2025-05-07T12:00:00Z",
                "views": 42,
                "download_links": ["magnet:?xt=urn:btih:..."]
            }
        }
        # backward compatibility with Pydantic v1
        schema_extra = json_schema_extra
