# scrapers/cicada.py

import logging
import re
from typing import Any, Dict, List
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError,
)

from scrapers.base import BaseScraper
from scrapers.config import ScraperConfig

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class CicadaScraper(BaseScraper):
    slug = "cicada"
    JS_WAIT_SELECTOR = "div.flex.flex-wrap"

    def _get_client_key(self, config: ScraperConfig) -> str:
        """
        Usa Playwright para passar pelo challenge JS (anti-DDoS),
        aguarda o JS_WAIT_SELECTOR e retorna o cookie 'clientKey'.
        """
        launch_args: Dict[str, Any] = {"headless": True}
        if config.url.endswith(".onion") or config.bypass_config.use_proxies:
            launch_args["proxy"] = {"server": self.TOR_PROXY}
            logger.info("Playwright: usando proxy TOR %s", self.TOR_PROXY)

        logger.info("Playwright: iniciando Chromium headless…")
        with sync_playwright() as pw:
            browser = pw.chromium.launch(**launch_args)
            ctx = browser.new_context(ignore_https_errors=True)
            page = ctx.new_page()
            logger.debug("Playwright: abrindo página %s", config.url)

            try:
                page.goto(
                    config.url,
                    wait_until="networkidle",
                    timeout=config.execution_options.timeout_seconds * 1000,
                )
                logger.debug("Playwright: aguardando seletor %r", self.JS_WAIT_SELECTOR)
                page.wait_for_selector(
                    selector=self.JS_WAIT_SELECTOR,
                    timeout=config.execution_options.timeout_seconds * 1000,
                )
                logger.info("Playwright: desafio JS concluído, fórum carregado")
            except PlaywrightTimeoutError as e:
                browser.close()
                logger.error("Playwright: falha no anti-DDoS inicial: %s", e)
                raise RuntimeError("Challenge JS inicial falhou") from e

            cookies = ctx.cookies()
            logger.debug("Playwright: cookies brutos recebidos: %s", cookies)
            browser.close()

        # procura o clientKey e log detalhado
        for c in cookies:
            logger.info(
                "Cookie encontrado → name=%s, value=%s, domain=%s, path=%s, expires=%s",
                c.get("name"),
                c.get("value"),
                c.get("domain"),
                c.get("path"),
                c.get("expires"),
            )
            if c.get("name") == "clientKey":
                logger.info("→ clientKey selecionado: %s", c["value"])
                return c["value"]

        logger.error("Nenhum cookie 'clientKey' encontrado entre os cookies acima")
        raise RuntimeError("Cookie clientKey não foi retornado pelo desafio JS")

    def run(self, config: ScraperConfig) -> List[Dict[str, Any]]:
        """
        1) Passa pelo anti-DDoS com Playwright e extrai clientKey
        2) Sobe Chromium e reutiliza o mesmo contexto para paginação
        3) Itera ?page=1,2,3… até não encontrar mais cards
        4) Parseia cada card e traz a descrição do post
        """
        # 1) Desafio JS e cookie
        client_key = self._get_client_key(config)

        # 2) Configura Playwright para a paginação
        launch_args: Dict[str, Any] = {"headless": True}
        if config.url.endswith(".onion") or config.bypass_config.use_proxies:
            launch_args["proxy"] = {"server": self.TOR_PROXY}
            logger.info("Playwright: usando proxy TOR %s", self.TOR_PROXY)

        results: List[Dict[str, Any]] = []
        logger.info("Iniciando paginação via Playwright…")

        with sync_playwright() as pw:
            browser = pw.chromium.launch(**launch_args)
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()

            # injeta manualmente o cookie no contexto
            domain = re.sub(r"https?://", "", config.url).split("/")[0]
            context.add_cookies([{
                "name": "clientKey",
                "value": client_key,
                "domain": domain,
                "path": "/",
            }])
            logger.debug("Cookie clientKey injetado no contexto para domínio %s", domain)

            page_num = 1
            while True:
                # monta a URL da page atual
                page_url = (
                    config.url
                    if page_num == 1
                    else f"{config.url}{'&' if '?' in config.url else '?'}page={page_num}"
                )
                logger.info("Página %d → %s", page_num, page_url)

                try:
                    page.goto(
                        page_url,
                        wait_until="networkidle",
                        timeout=config.execution_options.timeout_seconds * 1000,
                    )
                    page.wait_for_selector(
                        selector=self.JS_WAIT_SELECTOR,
                        timeout=config.execution_options.timeout_seconds * 1000,
                    )
                    logger.debug("Página %d carregada com sucesso", page_num)
                except PlaywrightTimeoutError:
                    logger.info("Seletor não encontrado na página %d – encerrando paginação", page_num)
                    break

                html = page.content()
                soup = BeautifulSoup(html, "html.parser")
                cards = soup.select("div.block.relative.p-8.bg-gray-800.rounded-lg")
                logger.info("Página %d possui %d cards", page_num, len(cards))
                if not cards:
                    logger.info("Nenhum card em page %d – fim da paginação", page_num)
                    break

                # parse de cada card
                for idx, card in enumerate(cards, start=1):
                    rec: Dict[str, Any] = {"page": page_num, "card_index": idx}
                    logger.debug("Parsing card %d da página %d", idx, page_num)

                    # título
                    h2 = card.find("h2")
                    rec["company"] = h2.get_text(strip=True) if h2 else ""
                    logger.debug(" → company: %s", rec["company"])

                    # web / post_url
                    rec["web"], rec["post_url"] = "", ""
                    for a in card.find_all("a", href=True):
                        href = a["href"]
                        txt = a.get_text(strip=True).upper()
                        if href.startswith("http"):
                            rec["web"] = href
                        elif "VIEW POST" in txt:
                            rec["post_url"] = urljoin(config.url, href)
                    logger.debug(" → web: %s, post_url: %s", rec["web"], rec["post_url"])

                    # extrai labels genéricos
                    def _ext(label: str) -> str:
                        sp = card.find(
                            "span", string=re.compile(fr"^{re.escape(label)}$", re.I)
                        )
                        if not sp or not sp.next_sibling:
                            return ""
                        return sp.next_sibling.get_text(strip=True)

                    rec["size_data"]   = _ext("size data:")
                    rec["attachments"] = _ext("Attachments:")
                    rec["created"]     = _ext("Created:")
                    logger.debug(
                        " → size_data=%s, attachments=%s, created=%s",
                        rec["size_data"], rec["attachments"], rec["created"],
                    )

                    # status
                    st = card.find("span", class_="timer")
                    rec["status"] = {
                        "id":        st.get("id", "") if st else "",
                        "end_date":  st.get("data-end-date", "") if st else "",
                        "remaining": st.get_text(strip=True) if st else "",
                    }
                    logger.debug(" → status=%s", rec["status"])

                    # views
                    v = card.select_one("div.absolute.bottom-0 p.text-sm")
                    txt = v.get_text(strip=True) if v else ""
                    rec["views"] = int(txt) if txt.isdigit() else 0
                    logger.debug(" → views=%d", rec["views"])

                    # descrição do post
                    rec["description"] = ""
                    if rec["post_url"]:
                        logger.debug(" → buscando descrição em %s", rec["post_url"])
                        try:
                            page.goto(
                                rec["post_url"],
                                wait_until="networkidle",
                                timeout=10_000,
                            )
                            page.wait_for_selector(
                                selector="div.pr-10.flex-grow",
                                timeout=5_000,
                            )
                            det_soup = BeautifulSoup(page.content(), "html.parser")
                            p = det_soup.select_one("div.pr-10.flex-grow p")
                            rec["description"] = p.get_text(strip=True) if p else ""
                            logger.debug(" → description capturada (%d chars)", len(rec["description"]))
                        except PlaywrightTimeoutError:
                            logger.warning(" → falhou ao carregar detalhe %s", rec["post_url"])

                    results.append(rec)

                page_num += 1

            browser.close()

        logger.info("Scraping CICADA finalizado com %d registros", len(results))
        return results
