import asyncio
import json
import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Error as PwError

from .base import BaseScraper

TOPIC_RX = re.compile(r"viewtopic\('([^']+)'\)")

class PlayNewsScraper(BaseScraper):
    slug = "playnews"

    def scrape(self, site, db) -> list[dict]:
        """
        Retorna uma lista de dicts com os campos do LeakDoc.
        """
        try:
            return asyncio.run(self._scrape(site, db))
        except PwError as e:
            if "ERR_SOCKS_CONNECTION_FAILED" in str(e):
                return []
            raise

    async def _scrape(self, site, db) -> list[dict]:
        leaks: list[dict] = []
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            ctx = await browser.new_context(proxy={"server": self.TOR_PROXY})
            page = await ctx.new_page()
            page.set_default_timeout(120_000)

            page_num = 1
            while True:
                list_url = f"{site.url.rstrip('/')}/index.php?page={page_num}"
                await page.goto(list_url, wait_until="networkidle")
                await self._snapshot(page, site.id, db)

                soup = BeautifulSoup(await page.content(), "html.parser")
                cards = soup.select("th.News")
                if not cards:
                    break

                for card in cards:
                    m = TOPIC_RX.search(card.get("onclick", ""))
                    if not m:
                        continue
                    tid = m.group(1)

                    title = card.find(text=True, recursive=False).strip()
                    country = (
                        card.select_one("i.location").next_sibling.strip()
                        if card.select_one("i.location") else None
                    )
                    txt = card.get_text(" ", strip=True)
                    views = int(re.search(r"views:\s*(\d+)", txt).group(1))
                    added = datetime.fromisoformat(
                        re.search(r"added:\s*(\d{4}-\d{2}-\d{2})", txt).group(1)
                    ).replace(tzinfo=timezone.utc)
                    pub_date = datetime.fromisoformat(
                        re.search(r"publication date:\s*(\d{4}-\d{2}-\d{2})", txt).group(1)
                    ).replace(tzinfo=timezone.utc)

                    detail_url = f"{site.url.rstrip('/')}/topic.php?id={tid}"
                    await page.goto(detail_url, wait_until="networkidle")
                    await self._snapshot(page, site.id, db, save_html=True)
                    detail_txt = BeautifulSoup(await page.content(), "html.parser").get_text(" ", strip=True)

                    amt = re.search(r"amount of data:\s*([^ ]+)", detail_txt, re.IGNORECASE)
                    amount_of_data = amt.group(1) if amt else None

                    info = re.search(
                        r"information:\s*(.+?)comment:", detail_txt, re.IGNORECASE | re.DOTALL
                    )
                    information = info.group(1).strip() if info else None

                    comm = re.search(
                        r"comment:\s*(.+?)(?:DOWNLOAD LINKS:|$)",
                        detail_txt,
                        re.IGNORECASE | re.DOTALL
                    )
                    comment = comm.group(1).strip() if comm else None

                    download_links = re.findall(r"https?://[^\s]+\.onion/[^\s]+", detail_txt)
                    rar = re.search(r"Rar password:\s*([^\s]+)", detail_txt, re.IGNORECASE)
                    rar_password = rar.group(1) if rar else None

                    leaks.append({
                        "site_id":          site.id,
                        "company":          title,
                        "country":          country,
                        "found_at":         added,
                        "source_url":       detail_url,
                        "views":            views,
                        "publication_date": pub_date,
                        "amount_of_data":   amount_of_data,
                        "information":      information,
                        "comment":          comment,
                        "download_links":   json.dumps(download_links),
                        "rar_password":     rar_password,
                    })

                page_num += 1

            await browser.close()
        return leaks
