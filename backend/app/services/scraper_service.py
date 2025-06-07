import logging
import asyncio
import json
from sqlalchemy.orm import Session

from scrapers import registry
from scrapers.config import ScraperConfig, BypassConfig, Credentials, TorOptions, ExecutionOptions
from db.models.site_metrics import SiteMetrics
from db.models.scrape_log import ScrapeLog
from repository.leaks_mongo import insert_leak
from schemas.leak_mongo import LeakDoc
from core.config import settings

logger = logging.getLogger(__name__)


def _build_config(site, url: str, payload: dict | None) -> ScraperConfig:
    bypass = None
    creds = None
    if site.bypass_config:
        try:
            bypass = BypassConfig(**json.loads(site.bypass_config))
        except Exception:
            bypass = None
    if site.credentials:
        try:
            creds = Credentials(**json.loads(site.credentials))
        except Exception:
            creds = None
    if payload:
        if payload.get("bypassConfig"):
            bypass = BypassConfig(**payload["bypassConfig"])
        if payload.get("credentials"):
            creds = Credentials(**payload["credentials"])
    bypass = bypass or BypassConfig(use_proxies=False, rotate_user_agent=False)
    tor = TorOptions(max_retries=settings.TOR_MAX_RETRIES, retry_interval=settings.TOR_RETRY_INTERVAL)
    exec_opts = ExecutionOptions(max_retries=settings.TOR_MAX_RETRIES, timeout_seconds=60)
    return ScraperConfig(
        site_id=site.id,
        type=site.type.value if hasattr(site.type, "value") else site.type,
        url=url,
        bypass_config=bypass,
        credentials=creds,
        tor=tor,
        execution_options=exec_opts,
    )


def run_scraper_for_site(site, db: Session, payload: dict | None = None) -> int:
    """Executa o scraper para cada link do site."""
    if not site.enabled:
        logger.info("Site %s está desabilitado, pulando.", site.url)
        return 0

    scraper = registry.get(site.scraper)
    if not scraper:
        raise RuntimeError(f"Scraper '{site.scraper}' não encontrado")

    urls = [l.url for l in site.links] or [site.url]
    total_inserted = 0
    for url in urls:
        config = _build_config(site, url, payload)
        try:
            raw_leaks = scraper.run(config)
        except Exception as exc:
            db.add(SiteMetrics(site_id=site.id, retries=getattr(scraper, "last_retries", 0), permanent_fail=True))
            db.add(ScrapeLog(site_id=site.id, url=url, success=False, message=str(exc)))
            db.commit()
            logger.exception("Scraper failure for %s", url)
            continue

        inserted = 0
        for data in raw_leaks:
            doc = data if isinstance(data, LeakDoc) else LeakDoc(**data)
            asyncio.run(insert_leak(doc))
            inserted += 1

        total_inserted += inserted
        db.add(SiteMetrics(site_id=site.id, retries=getattr(scraper, "last_retries", 0), permanent_fail=False))
        db.add(ScrapeLog(site_id=site.id, url=url, success=True))
        db.commit()

    return total_inserted
