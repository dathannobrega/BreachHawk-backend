from __future__ import annotations
from datetime import datetime, timezone
from typing import List, Dict
from bs4 import BeautifulSoup

from .base import BaseScraper

class TelegramScraper(BaseScraper):
    """Scraper que coleta mensagens de canais do Telegram via HTML."""
    slug = "telegram"

    def parse(self, html: str) -> List[Dict]:
        soup = BeautifulSoup(html, "html.parser")
        leaks: List[Dict] = []
        for msg in soup.select("div.tgme_widget_message"):
            text_el = msg.select_one(".tgme_widget_message_text")
            if not text_el:
                continue
            msg_id = msg.get("data-post", "").split("/")[-1]
            timestamp_el = msg.select_one("time")
            found_at = datetime.now(timezone.utc)
            if timestamp_el and timestamp_el.has_attr("datetime"):
                try:
                    found_at = datetime.fromisoformat(timestamp_el["datetime"])
                except Exception:
                    pass
            leaks.append({
                "company": "telegram",
                "information": text_el.get_text(strip=True),
                "source_url": f"https://t.me/{msg_id}" if msg_id else None,
                "found_at": found_at,
            })
        return leaks
