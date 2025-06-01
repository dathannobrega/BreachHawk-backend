import asyncio
import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Error as PwError

from scrapers.base import ScraperBase

DATE_RX = re.compile(r"(\d{2}/\d{2}/\d{4})")

class RansomHouseScraper(ScraperBase):
    slug = "ransomhouse"

    async def _fetch_html_and_snap(self, url: str, site_id: int, db, timeout: int = 120_000) -> str:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            ctx = await browser.new_context(proxy={"server": self.TOR_PROXY})
            page = await ctx.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=timeout)

            # salva PNG + (opcional) HTML no Postgres
            await self._snapshot(page, site_id, db)

            html = await page.content()
            await browser.close()
            return html

    def scrape(self, site, db) -> list[dict]:
        """
        Retorna uma lista de dicts com os campos do LeakDoc.
        """
        try:
            html = asyncio.run(self._fetch_html_and_snap(site.url, site.id, db))
        except PwError as e:
            if "ERR_SOCKS_CONNECTION_FAILED" in str(e):
                return []
            raise

        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select("div.cls_record")
        if not cards:
            return []

        leaks: list[dict] = []
        for card in cards:
            title_el = card.select_one("div.cls_recordTop > p")
            if not title_el:
                continue
            company = title_el.get_text(strip=True)

            a_tag = card.find("a", href=True)
            source_url = site.url.rstrip("/") + a_tag["href"] if a_tag else site.url

            m = DATE_RX.search(card.get_text(" ", strip=True))
            found_at = (
                datetime.strptime(m.group(1), "%d/%m/%Y").replace(tzinfo=timezone.utc)
                if m else datetime.now(timezone.utc)
            )

            leaks.append({
                "site_id":    site.id,
                "company":    company,
                "country":    None,
                "found_at":   found_at,
                "source_url": source_url,
            })

        return leaks
