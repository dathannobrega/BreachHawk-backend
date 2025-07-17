import re
import asyncio
from datetime import datetime, timezone
from typing import List, Dict
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from scrapers.base import BaseScraper
from scrapers.config import ScraperConfig

CLI_CMD = "leaks"
MAGNET_RX = re.compile(r"magnet:\?xt=urn:btih:[^\s]+", re.I)


class AkiraCLIScraper(BaseScraper):
    slug = "akira_site"
    JS_WAIT_SELECTOR = "pre, table"

    async def _fetch_headless(self, config: ScraperConfig) -> str:
        # Usa Playwright via BaseScraper, respeitando proxies e timeouts
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            kwargs = {}
            # aplica proxy TOR se necessário
            if config.url.endswith(".onion") or config.bypass_config.use_proxies:
                kwargs["proxy"] = {"server": self.TOR_PROXY}
            context = await browser.new_context(**kwargs)
            page = await context.new_page()

            # Navega até a URL com timeout configurável
            await page.goto(
                config.url,
                timeout=config.execution_options.timeout_seconds * 1000,
                wait_until="domcontentloaded",
            )
            # Dispara o comando CLI no terminal embutido
            await page.keyboard.type(CLI_CMD)
            await page.keyboard.press("Enter")

            # Aguarda o output aparecer
            await page.wait_for_selector(
                self.JS_WAIT_SELECTOR,
                timeout=config.execution_options.timeout_seconds * 1000,
            )
            content = await page.content()
            await browser.close()
            return content

    def run(self, config: ScraperConfig) -> List[Dict]:
        # Garante uso de JS para executar o CLI
        config.needs_js = True
        html = self.fetch(config)
        leaks = self.parse(html)

        # Adiciona site_id e converte URLs relativas
        base = config.url.rstrip("/") + "/"
        for leak in leaks:
            leak.setdefault("site_id", config.site_id)
            url = leak.get("source_url")
            if url and not url.startswith("http"):
                leak["source_url"] = urljoin(base, url.lstrip("/"))
        return leaks

    def parse(self, html: str) -> List[Dict]:
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.select("table tr")[1:]
        leaks: List[Dict] = []
        for tr in rows:
            cols = [c.get_text(" ", strip=True) for c in tr.find_all("td")]
            if len(cols) < 4:
                continue

            company = cols[0]
            magnet_match = MAGNET_RX.search(tr.text)
            link = magnet_match.group(0) if magnet_match else cols[3]
            found_at = datetime.now(timezone.utc)

            leaks.append({
                "company": company,
                "source_url": link,
                "found_at": found_at,
            })
        return leaks
