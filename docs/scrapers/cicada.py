# scrapers/cicada.py

import logging
import re
from typing import Any, Dict, List
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from scrapers.base import BaseScraper
from scrapers.config import ScraperConfig

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class CicadaScraper(BaseScraper):
    slug = "cicada"
    # herda TOR_PROXY, JS_WAIT_SELECTOR e USER_AGENTS do BaseScraper

    def run(self, config: ScraperConfig) -> List[Dict[str, Any]]:
        """
        1) Cria session (UA + proxy/TOR) com _build_session
        2) GET inicial para gravar clientKey
        3) Loop paginado (?page=N) até não encontrar mais cards
        4) Parse de cada card + fetch de detalhe para 'description'
        """
        session = self._build_session(config)

        # GET inicial: carrega clientKey no cookie
        logger.info("Inicializando sessão em %s", config.url)
        init_resp = session.get(
            config.url, timeout=config.execution_options.timeout_seconds
        )
        init_resp.raise_for_status()
        logger.debug("Cookies após init: %s", session.cookies.get_dict())

        results: List[Dict[str, Any]] = []
        page_num = 1

        while True:
            # monta URL da página
            if page_num == 1:
                page_url = config.url
            else:
                sep = "&" if "?" in config.url else "?"
                page_url = f"{config.url}{sep}page={page_num}"

            logger.info("Buscando página %d: %s", page_num, page_url)
            resp = session.get(page_url, timeout=config.execution_options.timeout_seconds)
            resp.raise_for_status()
            html = resp.text

            # se o selector de grid não existir, encerra paginação
            if self.JS_WAIT_SELECTOR and self.JS_WAIT_SELECTOR not in html:
                logger.info(
                    "Selector %r não encontrado na página %d – fim da paginação",
                    self.JS_WAIT_SELECTOR,
                    page_num,
                )
                break

            soup = BeautifulSoup(html, "html.parser")
            cards = soup.select("div.block.relative.p-8.bg-gray-800.rounded-lg")
            if not cards:
                logger.info("Nenhum card na página %d – fim da paginação", page_num)
                break

            for card in cards:
                record: Dict[str, Any] = {
                    "page": page_num,
                    "source_url": page_url,
                }

                # título
                title_el = card.find("h2")
                record["company"] = title_el.get_text(strip=True) if title_el else ""

                # web_url e post_url
                record["web"] = ""
                record["post_url"] = ""
                for a in card.find_all("a", href=True):
                    href = a["href"]
                    text = a.get_text(strip=True)
                    if href.startswith("http"):
                        record["web"] = href
                    elif "VIEW POST" in text.upper():
                        record["post_url"] = urljoin(config.url, href)

                # helper para extrair valor após <span>label</span><span>valor</span>
                def _extract(label: str) -> str:
                    span = card.find(
                        "span", string=re.compile(fr"^{re.escape(label)}$", re.I)
                    )
                    if not span:
                        raise ValueError(f"Label {label} não encontrado")
                    sibling = span.find_next_sibling("span")
                    return sibling.get_text(strip=True) if sibling else ""

                # size_data, attachments, created
                try:
                    record["size_data"] = _extract("size data:")
                except ValueError:
                    record["size_data"] = ""
                try:
                    record["attachments"] = _extract("Attachments:")
                except ValueError:
                    record["attachments"] = ""
                try:
                    record["created"] = _extract("Created:")
                except ValueError:
                    record["created"] = ""

                # status
                status_span = card.find("span", class_="timer")
                if status_span:
                    record["status"] = {
                        "id": status_span.get("id", ""),
                        "end_date": status_span.get("data-end-date", ""),
                        "remaining": status_span.get_text(strip=True),
                    }
                else:
                    record["status"] = {}

                # views
                view_el = card.select_one("div.absolute.bottom-0 p.text-sm")
                views_txt = view_el.get_text(strip=True) if view_el else ""
                record["views"] = int(views_txt) if views_txt.isdigit() else 0

                # fetch + parse detalhe (description)
                if record["post_url"]:
                    try:
                        det_resp = session.get(
                            record["post_url"],
                            timeout=config.execution_options.timeout_seconds,
                        )
                        det_resp.raise_for_status()
                        det_soup = BeautifulSoup(det_resp.text, "html.parser")
                        container = det_soup.select_one("div.pr-10.flex-grow")
                        if container:
                            p = container.find("p")
                            record["description"] = p.get_text(strip=True) if p else ""
                        else:
                            record["description"] = ""
                    except Exception as e:
                        logger.error(
                            "Erro ao buscar detalhe %s: %s", record["post_url"], e
                        )
                        record["description"] = ""
                else:
                    record["description"] = ""

                results.append(record)

            page_num += 1

        return results
