from __future__ import annotations
from datetime import datetime, timezone
from typing import List, Dict, Any
import logging
import asyncio

from telethon import TelegramClient, errors
from telethon.sessions import StringSession
from telethon.tl.types import Message
from telethon.tl.functions.channels import JoinChannelRequest

from scrapers.base import BaseScraper
from leaks.documents import LeakDoc
from sites.models import Site, TelegramAccount, SiteMetrics

logger = logging.getLogger(__name__)

GROUPS = [
  {
    "peer_type": "Channel",
    "tipo": "channel",
    "id": 1518255631,
    "title": "Data Leak Monitor",
    "username": "breachdetector",
    "is_forum": False,
    "linked_chat_id": None
  },
  {
    "peer_type": "Channel",
    "tipo": "channel",
    "id": 2637580579,
    "title": "DarkForums",
    "username": None,
    "is_forum": False,
    "linked_chat_id": 1806390689
  },
  {
    "peer_type": "Channel",
    "tipo": "supergroup",
    "id": 2598879907,
    "title": "COMBO",
    "username": "Combo445544",
    "is_forum": False
  },
  {
    "peer_type": "Channel",
    "tipo": "channel",
    "id": 1861685334,
    "title": "BaseLeak",
    "username": "baseleeak",
    "is_forum": False,
    "linked_chat_id": None
  },
  {
    "peer_type": "Channel",
    "tipo": "channel",
    "id": 1668004060,
    "title": "Data Globe",
    "username": None,
    "is_forum": False,
    "linked_chat_id": None
  },
  {
    "peer_type": "Channel",
    "tipo": "channel",
    "id": 2497466912,
    "title": "Marketplace |DataLeaky",
    "username": None,
    "is_forum": False,
    "linked_chat_id": None
  },
  {
    "peer_type": "Channel",
    "tipo": "channel",
    "id": 1981900014,
    "title": "黑暗军队",
    "username": "D4RKLE4K",
    "is_forum": False,
    "linked_chat_id": None
  },
  {
    "peer_type": "Channel",
    "tipo": "channel",
    "id": 2876409589,
    "title": "黑暗军队",
    "username": "D4RKLE4KS",
    "is_forum": False,
    "linked_chat_id": None
  },
  {
    "peer_type": "Channel",
    "tipo": "channel",
    "id": 2152660930,
    "title": "STUXNET - ستوكسنت",
    "username": "xstuxnet",
    "is_forum": False,
    "linked_chat_id": None
  },
  {
    "peer_type": "Channel",
    "tipo": "channel",
    "id": 1877740020,
    "title": "Bucket Leaks",
    "username": None,
    "is_forum": False,
    "linked_chat_id": None
  }
]

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

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return TelegramClient(
            StringSession(account.session_string),
            account.api_id,
            account.api_hash,
            loop=loop,
        )
    async def _get_entity(self, client: TelegramClient, group: dict) -> Any:
        if group.get("username"):
            entity = await client.get_entity(group["username"])
        else:
            entity = await client.get_entity(group["id"])
        return entity

    async def _ensure_in_group(self, client: TelegramClient, group: dict) -> None:
        try:
            await self._get_entity(client, group)
        except errors.UserNotParticipantError:
            try:
                if group.get("username"):
                    await client(JoinChannelRequest(group["username"]))
                else:
                    logger.warning(
                        f"Não é possível entrar em grupo/canal sem username: {group}"
                    )
            except Exception as exc:
                logger.warning(f"Falha ao entrar no grupo {group}: {exc}")
        except Exception as exc:
            logger.warning(f"Erro ao verificar grupo {group}: {exc}")

    def parse(self, config) -> List[Any]:
        logger.info(f"Parsing Telegram messages for site: {config.site_id}")
        site = Site.objects.get(id=config.site_id)
        account = self._get_telegram_account(site)
        client = self._init_client(account)
        logger.info(f"Initialized Telegram client for account: {account}")

        loop = client.loop

        async def _parse() -> List[LeakDoc]:
            leaks: List[LeakDoc] = []
            async with client:
                for group in GROUPS:
                    logger.info(f"Processing entity: {group}")
                    if group.get("username") is None:
                        logger.warning(f"Group {group} não possui username")
                        continue

                    await self._ensure_in_group(client, group)
                    entity = await self._get_entity(client, group)
                    group_id = group["id"]
                    temp_leaks: List[LeakDoc] = []
                    async for message in client.iter_messages(entity, limit=100):
                        if not message.message:
                            continue
                        leak = LeakDoc(
                            site_id=site.id,
                            company="telegram",
                            source_url=f"https://t.me/c/{group_id}/{message.id}",
                            found_at=message.date.replace(tzinfo=timezone.utc),
                            information=message.message,
                        )
                        temp_leaks.append(leak)
                    leaks.extend(temp_leaks)
                logger.info(f"Found {len(leaks)} leaks")
            return leaks

        try:
            leaks = loop.run_until_complete(_parse())
        except errors.SessionPasswordNeededError:
            logger.error("Session string precisa de autenticação 2FA. Gere manualmente.")
            SiteMetrics.objects.create(site=site, permanent_fail=True)
            leaks = []
        except errors.AuthKeyUnregisteredError:
            logger.error("Session string inválida ou expirada. Gere nova session_string.")
            SiteMetrics.objects.create(site=site, permanent_fail=True)
            leaks = []
        except Exception as exc:
            logger.error(f"Erro ao coletar mensagens do Telegram: {exc}")
            SiteMetrics.objects.create(site=site, permanent_fail=True)
            leaks = []
        finally:
            loop.close()

        return leaks

    def fetch(self, config):
        return config

    def run(self, config):
        return self.parse(config)