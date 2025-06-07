# backend/celery_app.py

from celery import Celery, states
from celery.exceptions import Ignore
from core.config import settings
from core.logging_conf import configure_logging
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from db.session import SessionLocal
from db.models.site import Site
import structlog
from services.scraper_service import run_scraper_for_site

# Configura o structlog
configure_logging()
logger = structlog.get_logger(__name__)

# Instrumenta o Celery para tracing
CeleryInstrumentor().instrument()

celery_app = Celery(
    "tidw",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

def _fail(task, msg: str, exc_cls: str = "ValueError"):
    """
    Marca a task como FAILURE (usando o formato que o Celery espera)
    e interrompe o processamento.
    """
    logger.error("Celery Failure", task_id=task.request.id, message=msg)
    task.update_state(
        state=states.FAILURE,
        meta={
            "exc_type": exc_cls,
            "exc_message": msg,
            "exc_module": "builtins",
        },
    )
    raise Ignore()

@celery_app.task(bind=True, name="scrape_site")
def scrape_site(self, payload: dict) -> dict:
    """
    Executa o scraper para um site específico e retorna {"inserted": N}.
    """
    # Em vez de usar 'with logger.bind(...)', vinculamos o logger explicitamente
    site_id = payload.get("siteId") if isinstance(payload, dict) else payload
    bound_logger = logger.bind(task="scrape_site", site_id=site_id)

    with SessionLocal() as db:
        site = db.get(Site, site_id)
        if not site or not site.enabled:
            return _fail(self, "Site não encontrado ou desabilitado")

        try:
            inserted = run_scraper_for_site(site, db, payload)
            return {"inserted": inserted}

        except Exception as exc:
            # Usa o logger vinculado para registrar a exceção
            bound_logger.exception("Exception in scrape_site", error=str(exc))
            return _fail(self, str(exc), exc_cls=exc.__class__.__name__)

@celery_app.task(name="scrape_all_sites")
def scrape_all_sites() -> int:
    """
    Executa o scraper em todos os sites habilitados (em sequência).
    """
    total = 0
    with SessionLocal() as db:
        for site in db.query(Site).filter_by(enabled=True):
            total += run_scraper_for_site(site, db)
    return total
