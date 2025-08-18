from __future__ import annotations
import abc
import logging
import random
import time
from typing import Dict, List, Dict as DictType, Optional

import requests
from requests import RequestException
from playwright.async_api import async_playwright
from django.conf import settings

from utils.tor import renew_tor_circuit
from .config import ScraperConfig

logger = logging.getLogger(__name__)

registry: Dict[str, "BaseScraper"] = {}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/118 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/15.6 Safari/605.1.15",
]


class FetchTimeout(Exception):
    pass


class BlockedByCaptcha(Exception):
    pass


class BaseScraper(abc.ABC):
    slug: str
    TOR_PROXY = settings.TOR_PROXY
    JS_WAIT_SELECTOR: Optional[str] = None

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        if hasattr(cls, "slug"):
            slug = getattr(cls, "slug")
            if slug in registry:
                raise RuntimeError(f"Scraper slug duplicado: {slug}")
            registry[slug] = cls()
            logger.debug("Scraper registrado: %s → %s", slug, cls.__name__)

    def _build_session(self, config: ScraperConfig) -> requests.Session:
        session = requests.Session()
        if config.bypass_config is None:
            config.bypass_config = BypassConfig(use_proxies=False, rotate_user_agent=False)

        ua = (
            random.choice(USER_AGENTS)
            if config.bypass_config.rotate_user_agent
            else "BreachHawkBot/1.0"
        )
        session.headers.update({"User-Agent": ua})
        if config.url.endswith(".onion") or config.bypass_config.use_proxies:
            proxy = self.TOR_PROXY.replace("socks5://", "socks5h://")
            session.proxies.update({"http": proxy, "https": proxy})
        return session

    async def _fetch_headless(self, config: ScraperConfig) -> str:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            kwargs = {}
            if (
                config.url.endswith(".onion")
                or config.bypass_config is not None and config.bypass_config.use_proxies
            ):
                kwargs["proxy"] = {"server": self.TOR_PROXY}
            ctx = await browser.new_context(**kwargs)
            page = await ctx.new_page()
            await page.goto(
                config.url,
                timeout=config.execution_options.timeout_seconds * 1000,
                wait_until="networkidle",
            )
            if self.JS_WAIT_SELECTOR:
                try:
                    await page.wait_for_selector(
                        self.JS_WAIT_SELECTOR,
                        timeout=(
                            config.execution_options.timeout_seconds * 1000
                        ),
                    )
                except Exception:
                    logger.debug(
                        "Selector %s not found", self.JS_WAIT_SELECTOR
                    )
            html = await page.content()
            await browser.close()
            return html

    def fetch(self, config: ScraperConfig) -> str:
        last_exc: Optional[Exception] = None
        if config.needs_js:
            try:
                html = self._fetch_headless_sync(config)
                self.last_retries = 0
                return html
            except Exception as exc:
                last_exc = exc
                self.last_retries = 0
                raise last_exc
        for attempt in range(config.tor.max_retries + 1):
            if attempt:
                try:
                    renew_tor_circuit()
                except Exception:
                    logger.exception("Erro ao renovar circuito TOR")
                time.sleep(config.tor.retry_interval)
            try:
                session = self._build_session(config)
                resp = session.get(
                    config.url,
                    timeout=config.execution_options.timeout_seconds,
                )
                resp.raise_for_status()
                html = resp.text
                if "<html" not in html.lower():
                    raise ValueError("invalid html")
                self.last_retries = attempt
                return html
            except requests.Timeout as exc:
                last_exc = FetchTimeout(str(exc))
            except RequestException as exc:
                last_exc = exc
        try:
            html = self._fetch_headless_sync(config)
            self.last_retries = config.tor.max_retries + 1
            return html
        except Exception as exc:
            last_exc = exc
            self.last_retries = config.tor.max_retries + 1
        raise last_exc or RuntimeError("fetch failed")

    def _fetch_headless_sync(self, config: ScraperConfig) -> str:
        import asyncio
        return asyncio.run(self._fetch_headless(config))

    @abc.abstractmethod
    def parse(self, html: str) -> List[DictType]:
        ...

    def run(self, config: ScraperConfig) -> List[DictType]:
        html = self.fetch(config)
        return self.parse(html)
