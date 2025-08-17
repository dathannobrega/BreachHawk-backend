from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List

from telethon.sessions import StringSession
from telethon.sync import TelegramClient

from .base import BaseScraper
from .config import ScraperConfig


class TelegramScraper(BaseScraper):
    """Scraper que coleta mensagens de grupos do Telegram via Telethon."""

    slug = "telegram"

    def parse(self, html: str) -> List[Dict]:  # pragma: no cover - not used
        return []

    def run(self, config: ScraperConfig) -> List[Dict]:
        """Fetch messages from a Telegram group using Telethon."""
        from sites.models import Site, SiteMetrics

        site = Site.objects.select_related("telegram_account").get(
            pk=config.site_id
        )
        account = site.telegram_account
        if not account:
            raise RuntimeError("Telegram account not configured")

        session = StringSession(account.session_string or "")
        client = TelegramClient(session, account.api_id, account.api_hash)
        self.last_retries = 0

        try:
            with client:
                if not client.is_user_authorized():
                    if not account.phone:
                        raise RuntimeError("Telegram login required")
                    client.start(phone=account.phone)
                    account.session_string = client.session.save()
                    account.save(update_fields=["session_string"])

                entity = client.get_entity(config.url)
                leaks: List[Dict] = []
                for msg in client.iter_messages(entity):
                    if not getattr(msg, "message", None):
                        continue
                    link = getattr(msg, "message_link", None) or getattr(
                        msg, "link", None
                    )
                    if not link:
                        username = getattr(entity, "username", None)
                        if username:
                            link = f"https://t.me/{username}/{msg.id}"
                        else:
                            entity_id = abs(getattr(entity, "id", 0))
                            link = f"https://t.me/c/{entity_id}/{msg.id}"
                    found_at = msg.date
                    if (
                        isinstance(found_at, datetime)
                        and found_at.tzinfo is None
                    ):
                        found_at = found_at.replace(tzinfo=timezone.utc)
                    leaks.append(
                        {
                            "site_id": config.site_id,
                            "company": site.name,
                            "information": msg.message,
                            "source_url": link,
                            "found_at": found_at,
                        }
                    )
                return leaks
        except Exception:
            SiteMetrics.objects.create(
                site=site, retries=self.last_retries, permanent_fail=True
            )
            raise
