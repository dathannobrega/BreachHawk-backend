import time
import logging
import asyncio
from sqlalchemy.orm import Session
from scrapers import registry
from db.models.site_metrics import SiteMetrics
from core.config import settings
import requests
from playwright.async_api import TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError

from repository.leaks_mongo import insert_leak
from schemas.leak_mongo import LeakDoc

logger = logging.getLogger(__name__)

def run_scraper_for_site(site, db: Session) -> int:
   """
   Executa o scraper para o site, insere cada leak no MongoDB
   e registra métrica no PostgreSQL.
   Retorna quantos leaks foram inseridos no Mongo.
   """
   if not site.enabled:
       logger.info("Site %s está desabilitado, pulando.", site.url)
       return 0

   scraper = registry.get(site.scraper)
   if not scraper:
       raise RuntimeError(f"Scraper '{site.scraper}' não encontrado")

   max_retries = settings.TOR_MAX_RETRIES
   interval    = settings.TOR_RETRY_INTERVAL
   last_exc    = None

   for attempt in range(1, max_retries + 2):
       try:
           # agora o scraper deve retornar uma lista de dicts ou LeakDoc
           raw_leaks = scraper.scrape(site, db)
           inserted = 0

           for data in raw_leaks:
               # se vier dict, converte; se já for LeakDoc, passa direto
               doc = data if isinstance(data, LeakDoc) else LeakDoc(**data)
               asyncio.run(insert_leak(doc))
               inserted += 1

           # registra métrica de sucesso no PostgreSQL
           m = SiteMetrics(site_id=site.id, retries=attempt-1, permanent_fail=False)
           db.add(m)
           db.commit()

           return inserted

       except (requests.RequestException, asyncio.TimeoutError, PlaywrightTimeoutError) as exc:
           last_exc = exc

       except PlaywrightError as exc:
           if "ERR_TIMED_OUT" in str(exc):
               last_exc = exc
           else:
               raise

       # se não for retryable ou esgotou tentativas
       if not site.url.endswith(".onion") or attempt > max_retries:
           m = SiteMetrics(site_id=site.id, retries=attempt-1, permanent_fail=True)
           db.add(m); db.commit()
           logger.error("Falha permanente em %s: %s", site.url, last_exc)
           raise last_exc

       # retry: renova circuito TOR e aguarda
       logger.warning(
           "Attempt %d/%d falhou em %s: %s — renovando circuito TOR e aguardando %.1fs",
           attempt, max_retries, site.url, last_exc, interval
       )
       try:
           from utils.tor import renew_tor_circuit
           renew_tor_circuit()
       except Exception:
           logger.exception("Erro ao renovar circuito TOR")
       time.sleep(interval)

   # todas as tentativas esgotadas
   m = SiteMetrics(site_id=site.id, retries=max_retries, permanent_fail=True)
   db.add(m); db.commit()
   logger.error("Todas as tentativas falharam para %s", site.url)
   raise last_exc or RuntimeError("Erro desconhecido no scraper")
