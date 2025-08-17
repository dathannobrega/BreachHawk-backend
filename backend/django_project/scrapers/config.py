from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Literal


@dataclass
class BypassConfig:
    use_proxies: Optional[bool] = False
    rotate_user_agent: Optional[bool] = False
    captcha_solver: Optional[str] = None


@dataclass
class Credentials:
    username: str
    password: str
    token: Optional[str] = None


@dataclass
class TorOptions:
    max_retries: int
    retry_interval: float


@dataclass
class ExecutionOptions:
    max_retries: int
    timeout_seconds: int


@dataclass
class ScraperConfig:
    site_id: int
    type: Literal["forum", "website", "telegram", "discord", "paste"]
    url: str
    bypass_config: Optional[BypassConfig]
    credentials: Optional[Credentials]
    tor: TorOptions
    execution_options: ExecutionOptions
    needs_js: bool = False
