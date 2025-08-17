from __future__ import annotations
from datetime import datetime, timezone
from typing import List, Dict, Any
import logging

from telethon import TelegramClient, errors
from telethon.sessions import StringSession
from telethon.tl.types import Message

from scrapers.base import BaseScraper
from leaks.documents import LeakDoc
from sites.models import Site, TelegramAccount, SiteMetrics

logger = logging.getLogger(__name__)

class TelegramScraper(BaseScraper):
    slug = "telegram"

    def _get_telegram_account(self, site: Site) -> TelegramAccount:
        account = site.telegram_account
        if not account:
            raise RuntimeError("Site não possui TelegramAccount associado")
        return account

    def _init_client(self, account: TelegramAccount) -> TelegramClient:
        if not account.session_string:
            raise RuntimeError("session_string ausente. Gere manualmente usando Telethon.")
        return TelegramClient(StringSession(account.session_string), account.api_id, account.api_hash)

    def _ensure_in_group(self, client: TelegramClient, group_id: int) -> None:
        try:
            entity = client.get_entity(group_id)
        except errors.UserNotParticipantError:
            try:
                client(JoinChannelRequest(group_id))
            except Exception as exc:
                logger.warning(f"Falha ao entrar no grupo {group_id}: {exc}")
        except Exception as exc:
            logger.warning(f"Erro ao verificar grupo {group_id}: {exc}")

    def parse(self, config) -> List[Any]:
        site = Site.objects.get(id=config.site_id)
        account = self._get_telegram_account(site)
        client = self._init_client(account)

        group_ids = getattr(config, "group_ids", None) or []
        if not group_ids:
            group_ids = site.bypass_config.get("telegram_group_ids", []) if site.bypass_config else []
        if not group_ids:
            raise RuntimeError("Nenhum grupo Telegram configurado para monitorar")

        leaks: List[LeakDoc] = []
        try:
            with client:
                for group_id in group_ids:
                    self._ensure_in_group(client, group_id)
                    for message in client.iter_messages(group_id, limit=100):
                        if not message.message:
                            continue
                        leak = LeakDoc(
                            site_id=site.id,
                            company="telegram",
                            source_url=f"https://t.me/c/{group_id}/{message.id}",
                            found_at=message.date.replace(tzinfo=timezone.utc),
                            information=message.message,
                        )
                        leaks.append(leak)
        except errors.SessionPasswordNeededError:
            logger.error("Session string precisa de autenticação 2FA. Gere manualmente.")
            SiteMetrics.objects.create(site=site, permanent_fail=True)
        except errors.AuthKeyUnregisteredError:
            logger.error("Session string inválida ou expirada. Gere nova session_string.")
            SiteMetrics.objects.create(site=site, permanent_fail=True)
        except Exception as exc:
            logger.error(f"Erro ao coletar mensagens do Telegram: {exc}")
            SiteMetrics.objects.create(site=site, permanent_fail=True)
        return leaks

    def fetch(self, config):
        return config

    def run(self, config):
        return self.parse(config)