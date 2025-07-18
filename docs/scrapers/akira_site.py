# scrapers/akira_site.py

import asyncio
import logging
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

# Configuração de logging
logging.basicConfig(
    format="%(asctime)s %(levelname)s/%(name)s: %(message)s",
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)

CLI_COMMAND = "leaks"


class AkiraSiteScraper(BaseScraper):
    slug = "akira_site"

    async def _fetch_with_playwright(self, config: ScraperConfig) -> List[Dict]:
        logger.info("=== Iniciando Playwright fetch para %s ===", config.url)
        launch_args = {"headless": True}
        if config.url.endswith(".onion") or config.bypass_config.use_proxies:
            launch_args["proxy"] = {"server": self.TOR_PROXY}
            logger.info("Usando proxy TOR: %s", launch_args["proxy"])

        async with async_playwright() as pw:
            logger.debug("Playwright iniciado")
            browser = await pw.chromium.launch(**launch_args)
            logger.debug("Browser lançado")
            context = await browser.new_context(ignore_https_errors=True)
            logger.debug("Contexto criado (ignore_https_errors=True)")
            page = await context.new_page()
            logger.debug("Nova página aberta")

            try:
                # 1) Carrega a página inicial
                logger.info("Navegando para %s …", config.url)
                await page.goto(
                    config.url,
                    wait_until="domcontentloaded",
                    timeout=config.execution_options.timeout_seconds * 1000,
                )
                logger.info("Página inicial carregada")

                # 2) Lê CSRF token imediatamente
                locator = page.locator('meta[name="csrf-token"]')
                csrf_token = await locator.get_attribute("content")
                logger.info("CSRF token capturado: %s", csrf_token)

                # 3) (Opcional) Liste cookies para debug
                cookies = await context.cookies()
                logger.debug("Cookies no contexto: %s", cookies)

                # 4) Dispara o comando CLI no terminal
                logger.info("Digitando comando CLI: %r", CLI_COMMAND)
                await page.keyboard.type(CLI_COMMAND)
                await page.keyboard.press("Enter")
                logger.info("Comando enviado, aguardando resposta do /l")

                # 5) Faz a requisição a /l com headers apropriados
                url_l = f"{config.url.rstrip('/')}/l"
                headers = {
                    "X-CSRF-Token": csrf_token or "",
                    "X-Requested-With": "XMLHttpRequest",
                    "Accept": "application/json",
                }
                logger.debug("Enviando GET %s com headers: %s", url_l, headers)
                resp: PWResponse = await page.request.get(
                    url=url_l,
                    headers=headers,
                    timeout=120_000,  # até 2 minutos
                )
                logger.info("Resposta recebida: HTTP %d", resp.status)

                if resp.status != 200:
                    text = await resp.text()
                    logger.error("Corpo da resposta de erro: %s", text[:500])
                    raise RuntimeError(f"HTTP {resp.status} ao chamar /l")

                # 6) Extrai JSON
                data = await resp.json()
                logger.info("JSON recebido: %d itens", len(data))

            except (PlaywrightTimeoutError, asyncio.TimeoutError) as e:
                logger.exception("Timeout ou erro Playwright: %s", e)
                raise RuntimeError(f"Erro capturando /l via Playwright: {e}") from e

            finally:
                logger.debug("Fechando contexto e browser")
                await context.close()
                await browser.close()

        # 7) Monta lista de leaks
        leaks: List[Dict] = []
        for idx, item in enumerate(data, 1):
            leak = {
                "company": item.get("name", "").strip(),
                "source_url": item.get("url"),
                "desc": item.get("desc"),
                "progress": item.get("progress"),
                "found_at": datetime.now(timezone.utc),
                "site_id": config.site_id,
            }
            logger.debug("Leak %d: %s", idx, leak)
            leaks.append(leak)

        logger.info("=== Playwright fetch concluído: %d leaks extraídos ===", len(leaks))
        return leaks

    def run(self, config: ScraperConfig) -> List[Dict]:
        logger.info("Run chamado para %s", config.url)
        config.needs_js = True
        leaks = asyncio.run(self._fetch_with_playwright(config))

        # Normaliza URLs relativas
        base = config.url.rstrip("/") + "/"
        for leak in leaks:
            url = leak["source_url"]
            if url and not url.startswith("http"):
                new_url = urljoin(base, url.lstrip("/"))
                logger.debug("Convertendo URL relativa %s → %s", url, new_url)
                leak["source_url"] = new_url

        logger.info("Run finalizada com %d leaks", len(leaks))
        return leaks
