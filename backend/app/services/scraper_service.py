import time
import logging
import asyncio
import types
from sqlalchemy.orm import Session
from scrapers import registry
from db.models.site_metrics import SiteMetrics
from db.models.scrape_log import ScrapeLog
from core.config import settings
import requests
from playwright.async_api import TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError

from repository.leaks_mongo import insert_leak
from schemas.leak_mongo import LeakDoc

logger = logging.getLogger(__name__)

def run_scraper_for_site(site, db: Session) -> int:
    """Executa o scraper tentando cada link cadastrado."""
    if not site.enabled:
        logger.info("Site %s está desabilitado, pulando.", site.url)
        return 0

    scraper = registry.get(site.scraper)
    if not scraper:
        raise RuntimeError(f"Scraper '{site.scraper}' não encontrado")

    urls = [l.url for l in site.links] or [site.url]
    for url in urls:
        max_retries = settings.TOR_MAX_RETRIES
        interval = settings.TOR_RETRY_INTERVAL
        last_exc = None

        for attempt in range(1, max_retries + 2):
            try:
                site_data = types.SimpleNamespace(id=site.id, url=url)
                raw_leaks = scraper.scrape(site_data, db)
                inserted = 0

                for data in raw_leaks:
                    doc = data if isinstance(data, LeakDoc) else LeakDoc(**data)
                    asyncio.run(insert_leak(doc))
                    inserted += 1

                db.add(SiteMetrics(site_id=site.id, retries=attempt - 1, permanent_fail=False))
                db.add(ScrapeLog(site_id=site.id, url=url, success=True))
                db.commit()
                return inserted

            except (requests.RequestException, asyncio.TimeoutError, PlaywrightTimeoutError) as exc:
                last_exc = exc

            except PlaywrightError as exc:
                if "ERR_TIMED_OUT" in str(exc):
                    last_exc = exc
                else:
                    raise

            if not url.endswith(".onion") or attempt > max_retries:
                db.add(SiteMetrics(site_id=site.id, retries=attempt - 1, permanent_fail=True))
                db.add(ScrapeLog(site_id=site.id, url=url, success=False, message=str(last_exc)))
                db.commit()
                logger.error("Falha permanente em %s: %s", url, last_exc)
                break

            logger.warning(
                "Attempt %d/%d falhou em %s: %s — renovando circuito TOR e aguardando %.1fs",
                attempt, max_retries, url, last_exc, interval,
            )
            try:
                from utils.tor import renew_tor_circuit
                renew_tor_circuit()
            except Exception:
                logger.exception("Erro ao renovar circuito TOR")
            time.sleep(interval)

    raise last_exc or RuntimeError("Erro desconhecido no scraper")
