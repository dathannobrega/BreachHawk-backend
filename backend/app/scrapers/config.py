from __future__ import annotations
from typing import Optional, Literal
from pydantic import BaseModel

class BypassConfig(BaseModel):
    use_proxies: bool
    rotate_user_agent: bool
    captcha_solver: Optional[str] = None

class Credentials(BaseModel):
    username: str
    password: str
    token: Optional[str] = None

class TorOptions(BaseModel):
    max_retries: int
    retry_interval: float

class ExecutionOptions(BaseModel):
    max_retries: int
    timeout_seconds: int

class ScraperConfig(BaseModel):
    site_id: int
    type: Literal['forum','website','telegram','discord','paste']
    url: str
    bypass_config: BypassConfig
    credentials: Optional[Credentials] = None
    tor: TorOptions
    execution_options: ExecutionOptions
