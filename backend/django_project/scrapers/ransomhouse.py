from __future__ import annotations
import re
from datetime import datetime, timezone
from typing import List, Dict
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from .config import ScraperConfig

from .base import BaseScraper

DATE_RX = re.compile(r"(\d{2}/\d{2}/\d{4})")


class RansomHouseScraper(BaseScraper):
    slug = "ransomhouse"
    JS_WAIT_SELECTOR = "div.cls_record"

    def run(self, config: ScraperConfig) -> List[Dict]:
        """Fetch page and return leaks with absolute URLs and site id."""
        html = self.fetch(config)
        leaks = self.parse(html)
        base = config.url.rstrip("/") + "/"
        for leak in leaks:
            leak.setdefault("site_id", config.site_id)
            url = leak.get("source_url")
            if url and not url.startswith("http"):
                leak["source_url"] = urljoin(base, url.lstrip("/"))
        return leaks

    def parse(self, html: str) -> List[Dict]:
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select("div.cls_record")
        leaks: List[Dict] = []
        for card in cards:
            title_el = card.select_one("div.cls_recordTop > p")
            if not title_el:
                continue
            company = title_el.get_text(strip=True)
            a_tag = card.find("a", href=True)
            source_url = a_tag["href"] if a_tag else None
            m = DATE_RX.search(card.get_text(" ", strip=True))
            found_at = (
                datetime.strptime(m.group(1), "%d/%m/%Y").replace(
                    tzinfo=timezone.utc
                ) if m else datetime.now(timezone.utc)
            )
            leaks.append({
                "company": company,
                "source_url": source_url,
                "found_at": found_at,
            })
        return leaks
