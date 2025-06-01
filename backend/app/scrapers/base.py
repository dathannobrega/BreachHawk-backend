# scrapers/base.py

from __future__ import annotations
import abc
import logging
from typing import Dict, Type

import requests
from playwright.async_api import Page

from core.config import settings   # ← importa o .env

logger = logging.getLogger(__name__)

registry: Dict[str, "ScraperBase"] = {}

class ScraperBase(abc.ABC):
    """Classe abstrata para plugins de scraping."""

    slug: str

    # Tor proxy vinda do .env
    TOR_PROXY = settings.TOR_PROXY

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        if hasattr(cls, "slug"):
            slug = getattr(cls, "slug")
            if slug in registry:
                raise RuntimeError(f"Scraper slug duplicado: {slug}")
            registry[slug] = cls()
            logger.debug("Scraper registrado: %s → %s", slug, cls.__name__)

    @staticmethod
    def _get_session(use_tor: bool = True, timeout: int = 30) -> requests.Session:
        s = requests.Session()
        s.headers.update({"User-Agent": "BreachHawkBot/1.0"})
        if use_tor:
            proxy = ScraperBase.TOR_PROXY.replace("socks5://", "socks5h://")
            s.proxies.update({"http": proxy, "https": proxy})
        s.timeout = timeout
        return s

    @abc.abstractmethod
    def scrape(self, site, db) -> int:
        ...

    async def _snapshot(
        self, page: Page, site_id: int, db, save_html: bool = False
    ) -> None:
        from db.models.snapshot import ScrapeSnapshot

        png = await page.screenshot(full_page=True, type="png")
        html = await page.content() if save_html else None

        snap = ScrapeSnapshot(site_id=site_id, screenshot=png, html=html)
        db.add(snap)
        db.commit()
