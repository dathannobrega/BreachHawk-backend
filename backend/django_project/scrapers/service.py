import logging
from typing import Dict, Optional, Union
from uuid import UUID

from django.conf import settings

from . import registry
from .config import (
    ScraperConfig,
    BypassConfig,
    Credentials,
    TorOptions,
    ExecutionOptions,
)
from sites.models import Site, SiteMetrics
from .models import ScrapeLog
from leaks.mongo_utils import insert_leak
from leaks.documents import LeakDoc
from celery.result import AsyncResult
from celery import states, current_app
from typing import Any

logger = logging.getLogger(__name__)


def _build_config(
    site: Site, url: str, payload: Optional[Dict]
) -> ScraperConfig:
    bypass = site.bypass_config or {}
    creds = site.credentials or None
    if payload:
        bypass = payload.get("bypassConfig", bypass)
        creds = payload.get("credentials", creds)
    bypass_cfg = (
        BypassConfig(**bypass)
        if isinstance(bypass, dict)
        else bypass
    )
    creds_cfg = Credentials(**creds) if isinstance(creds, dict) else None
    tor = TorOptions(
        max_retries=settings.TOR_MAX_RETRIES,
        retry_interval=settings.TOR_RETRY_INTERVAL,
    )
    exec_opts = ExecutionOptions(
        max_retries=settings.TOR_MAX_RETRIES,
        timeout_seconds=60,
    )
    return ScraperConfig(
        site_id=site.id,
        type=site.type,
        url=url,
        bypass_config=bypass_cfg,
        credentials=creds_cfg,
        tor=tor,
        execution_options=exec_opts,
        needs_js=site.needs_js,
    )


def run_scraper_for_site(site_id: int, payload: Optional[Dict] = None) -> int:
    site = Site.objects.get(pk=site_id)
    if not site.enabled:
        logger.info("Site %s está desabilitado", site.url)
        return 0

    scraper = registry.get(site.scraper)
    if not scraper:
        raise RuntimeError(f"Scraper '{site.scraper}' não encontrado")

    urls = [link.url for link in site.links.all()] or [site.url]
    total_inserted = 0
    for url in urls:
        config = _build_config(site, url, payload)
        try:
            raw_leaks = scraper.run(config)
        except Exception as exc:
            SiteMetrics.objects.create(
                site=site,
                retries=getattr(scraper, "last_retries", 0),
                permanent_fail=True,
            )
            ScrapeLog.objects.create(
                site=site, url=url, success=False, message=str(exc)
            )
            logger.exception("Scraper failure for %s", url)
            continue

        inserted = 0
        for data in raw_leaks:
            doc = data if isinstance(data, LeakDoc) else LeakDoc(**data)
            insert_leak(doc)
            inserted += 1

        total_inserted += inserted
        SiteMetrics.objects.create(
            site=site,
            retries=getattr(scraper, "last_retries", 0),
            permanent_fail=False,
        )
        ScrapeLog.objects.create(site=site, url=url, success=True)

    return total_inserted


def schedule_scraper(site_id: int) -> AsyncResult:
    """Schedule a Celery task to scrape a site."""
    site = Site.objects.get(pk=site_id)
    payload = {
        "siteId": site.id,
        "type": site.type,
        "url": site.url,
        "bypassConfig": site.bypass_config,
        "credentials": site.credentials,
    }
    return current_app.send_task("scrape_site", args=[payload])


def get_task_status(task_id: Union[str, UUID]) -> dict:
    """Return the status information for a Celery task."""
    task_id_str = str(task_id)
    result = AsyncResult(task_id_str, app=current_app)
    info: Any = result.result if result.state == states.SUCCESS else result.info
    if isinstance(info, BaseException):
        info = str(info)
    return {"task_id": task_id_str, "status": result.state, "result": info}