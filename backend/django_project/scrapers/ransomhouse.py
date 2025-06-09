from __future__ import annotations
import re
from datetime import datetime, timezone
from typing import List, Dict
from bs4 import BeautifulSoup

from .base import BaseScraper

DATE_RX = re.compile(r"(\d{2}/\d{2}/\d{4})")


class RansomHouseScraper(BaseScraper):
    slug = "ransomhouse"

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
