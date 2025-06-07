from __future__ import annotations
import asyncio
from datetime import timezone
from typing import List
from telethon import TelegramClient
from .base import ScraperBase

class TelegramScraper(ScraperBase):
    """Scraper que coleta mensagens de canais ou grupos do Telegram."""
    slug = "telegram"

    async def _scrape_async(self, site, account) -> List[dict]:
        client = TelegramClient(
            account.session_string or "scraper",
            account.api_id,
            account.api_hash,
        )
        await client.start()
        entity = await client.get_entity(site.url)
        leaks = []
        async for msg in client.iter_messages(entity, limit=50):
            if not msg.message:
                continue
            leaks.append({
                "site_id": site.id,
                "company": "telegram",
                "source_url": f"https://t.me/{site.url}/{msg.id}",
                "found_at": msg.date.replace(tzinfo=timezone.utc),
                "information": msg.message,
            })
        await client.disconnect()
        return leaks

    def scrape(self, site, db) -> List[dict]:
        account = getattr(site, "telegram_account", None)
        if not account:
            return []
        try:
            return asyncio.run(self._scrape_async(site, account))
        except Exception:
            return []
