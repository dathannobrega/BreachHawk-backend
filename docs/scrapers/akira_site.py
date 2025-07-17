import asyncio
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

CLI_COMMAND = "leaks"


class AkiraSiteScraper(BaseScraper):
    slug = "akira_site"

    async def _fetch_with_playwright(self, config: ScraperConfig) -> List[Dict]:
        # 1) Monta args para Chromium + TOR proxy
        launch_args = {"headless": True}
        if config.url.endswith(".onion") or config.bypass_config.use_proxies:
            launch_args["proxy"] = {"server": self.TOR_PROXY}

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(**launch_args)
            context = await browser.new_context(ignore_https_errors=True)
            page = await context.new_page()

            try:
                # 2) Vai para a página inicial
                await page.goto(
                    config.url,
                    wait_until="domcontentloaded",
                    timeout=config.execution_options.timeout_seconds * 1000,
                )

                # 3) Lê o CSRF token (sem esperar visibilidade)
                csrf_token = await page.locator('meta[name="csrf-token"]').get_attribute("content")

                # 4) Dispara o comando 'leaks'
                await page.keyboard.type(CLI_COMMAND)
                await page.keyboard.press("Enter")

                # 5) Faz a requisição para /l, com timeout maior (até 2 min = 120000 ms)
                resp: PWResponse = await page.request.get(
                    url=f"{config.url.rstrip('/')}/l",
                    headers={
                        "X-CSRF-Token": csrf_token or "",
                        "X-Requested-With": "XMLHttpRequest",
                        "Accept": "application/json",
                    },
                    timeout=120_000,
                )
                if resp.status != 200:
                    raise RuntimeError(f"HTTP {resp.status} ao chamar /l")
                data = await resp.json()

            except (PlaywrightTimeoutError, asyncio.TimeoutError) as e:
                raise RuntimeError(f"Erro capturando /l via Playwright: {e}") from e
            finally:
                await context.close()
                await browser.close()

        # 6) Monta lista de leaks
        leaks: List[Dict] = []
        for item in data:
            leaks.append({
                "company": item.get("name", "").strip(),
                "source_url": item.get("url"),
                "desc": item.get("desc"),
                "progress": item.get("progress"),
                "found_at": datetime.now(timezone.utc),
                "site_id": config.site_id,
            })
        return leaks

    def run(self, config: ScraperConfig) -> List[Dict]:
        config.needs_js = True
        leaks = asyncio.run(self._fetch_with_playwright(config))

        # normaliza URLs relativas
        base = config.url.rstrip("/") + "/"
        for leak in leaks:
            url = leak["source_url"]
            if url and not url.startswith("http"):
                leak["source_url"] = urljoin(base, url.lstrip("/"))

        return leaks
