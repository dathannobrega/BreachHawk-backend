# scrapers/akira_cli.py
import re
import asyncio
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from .base import BaseScraper  # caminho absoluto
from .config import ScraperConfig

CLI_CMD = "leaks"
MAGNET_RX = re.compile(r"magnet:\?xt=urn:btih:[^\s]+", re.I)

class AkiraCLIScraper(BaseScraper):
    slug = "akira_cli"

    async def _fetch_html(self, url: str) -> str:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(proxy={"server": self.TOR_PROXY})
            page = await context.new_page()

            await page.goto(url, wait_until="domcontentloaded")
            await page.keyboard.type(CLI_CMD)
            await page.keyboard.press("Enter")
            await page.wait_for_selector("pre, table", timeout=30_000)
            html = await page.content()
            await browser.close()
            return html

    def parse(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.select("table tr")[1:]
        leaks: list[dict] = []
        for tr in rows:
            cols = [c.get_text(" ", strip=True) for c in tr.find_all("td")]
            if len(cols) < 4:
                continue
            company = cols[0]
            magnet = MAGNET_RX.search(tr.text)
            link = magnet.group(0) if magnet else cols[3]

            leaks.append(
                {
                    "company": company,
                    "country": None,
                    "found_at": datetime.now(timezone.utc),
                    "source_url": link,
                }
            )
        return leaks

    def run(self, config: ScraperConfig) -> list[dict]:
        html = asyncio.run(self._fetch_html(config.url))
        return self.parse(html)
