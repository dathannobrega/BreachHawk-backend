# scrapers/akira_site.py

import asyncio
import logging
import re
from datetime import datetime, timezone
from typing import List, Dict
from urllib.parse import urljoin

from playwright.async_api import (
    async_playwright,
    TimeoutError as PlaywrightTimeoutError,
    Response as PWResponse,
)

from scrapers.base import BaseScraper
from scrapers.config import ScraperConfig

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

CLI_COMMAND = "leaks"
URL_RX = re.compile(r"(https?://[^\]\s]+)")


class AkiraSiteScraper(BaseScraper):
    slug = "akira_site"

    async def _fetch_with_playwright(self, config: ScraperConfig) -> List[Dict]:
        logger.info("=== Iniciando Playwright fetch para %s ===", config.url)
        launch_args = {"headless": True}
        if config.url.endswith(".onion") or config.bypass_config.use_proxies:
            launch_args["proxy"] = {"server": self.TOR_PROXY}
            logger.info("Usando proxy TOR: %s", launch_args["proxy"])

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(**launch_args)
            context = await browser.new_context(ignore_https_errors=True)
            page = await context.new_page()

            try:
                # Navega e dispara 'leaks'
                await page.goto(
                    config.url,
                    wait_until="domcontentloaded",
                    timeout=config.execution_options.timeout_seconds * 1000,
                )
                await page.keyboard.type(CLI_COMMAND)
                await page.keyboard.press("Enter")

                # Captura CSRF e faz GET /l
                csrf = await page.locator('meta[name="csrf-token"]').get_attribute("content")
                resp: PWResponse = await page.request.get(
                    url=f"{config.url.rstrip('/')}/l",
                    headers={
                        "X-CSRF-Token": csrf or "",
                        "X-Requested-With": "XMLHttpRequest",
                        "Accept": "application/json",
                    },
                    timeout=120_000,
                )
                if resp.status != 200:
                    text = await resp.text()
                    logger.error("Erro HTTP %d: %s", resp.status, text[:200])
                    raise RuntimeError(f"HTTP {resp.status} ao chamar /l")
                data = await resp.json()

            except (PlaywrightTimeoutError, asyncio.TimeoutError) as e:
                logger.exception("Erro na captura via Playwright")
                raise RuntimeError(f"Erro capturando /l via Playwright: {e}") from e
            finally:
                await context.close()
                await browser.close()

        # --- Aqui adaptamos para company, information e source_url ---
        leaks: List[Dict] = []
        for item in data:
            raw_url = item.get("url", "")
            m = URL_RX.search(raw_url)
            clean_url = m.group(1) if m else raw_url

            leak = {
                "company": item.get("name", "").strip(),
                "information": item.get("desc", "").strip(),
                "source_url": clean_url,
                "found_at": datetime.now(timezone.utc),
                "site_id": config.site_id,
            }
            logger.debug("Leak extraído: %s", leak)
            leaks.append(leak)

        logger.info("=== Concluído: %d leaks ===", len(leaks))
        return leaks

    def run(self, config: ScraperConfig) -> List[Dict]:
        config.needs_js = True
        leaks = asyncio.run(self._fetch_with_playwright(config))

        # Normaliza URLs relativas, se necessário
        base = config.url.rstrip("/") + "/"
        for leak in leaks:
            if leak["source_url"] and not leak["source_url"].startswith("http"):
                leak["source_url"] = urljoin(base, leak["source_url"].lstrip("/"))

        return leaks
