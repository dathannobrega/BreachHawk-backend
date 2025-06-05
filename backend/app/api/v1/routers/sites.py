from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from schemas.site import SiteCreate, SiteRead
from db import models
from db.models.site_link import SiteLink
from api.v1 import deps
from celery.result import AsyncResult
from celery_app import celery_app
from schemas.task import TaskResponse, TaskStatus
from db.models import Site
from api.v1.deps import get_db

from api.v1.deps import get_current_admin_user

router = APIRouter()


@router.post("/upload-scraper", status_code=201, tags=["Sites"])
def upload_scraper(
    file: UploadFile = File(...),
    _admin=Depends(get_current_admin_user),
):
    import os, uuid, importlib.util, sys
    directory = "app/scrapers/custom"
    os.makedirs(directory, exist_ok=True)

    ext = os.path.splitext(file.filename)[1]
    if ext != ".py":
        raise HTTPException(status_code=400, detail="Apenas arquivos .py")

    filename = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(directory, filename)
    with open(path, "wb") as out_file:
        out_file.write(file.file.read())

    # importa o módulo para registrar no registry
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    return {"msg": "scraper uploaded"}

@router.post("/", response_model=SiteRead, status_code=201)
def create_site(site_in: SiteCreate, db: Session = Depends(get_db), _admin=Depends(get_current_admin_user)):

    # Verifica se algum dos links já está cadastrado
    if db.query(SiteLink).filter(SiteLink.url.in_(site_in.links)).first():
        raise HTTPException(400, "Link já cadastrado")

    data = {
        "url": site_in.links[0],
        "auth_type": site_in.auth_type,
        "captcha_type": site_in.captcha_type,
        "scraper": site_in.scraper,
        "needs_js": site_in.needs_js,
    }
    site = Site(**data)
    db.add(site)
    db.commit(); db.refresh(site)

    for link in site_in.links:
        db.add(SiteLink(site_id=site.id, url=link))
    db.commit(); db.refresh(site)

    site_links = [sl.url for sl in site.links]
    return SiteRead(id=site.id, links=site_links,
                    auth_type=site.auth_type,
                    captcha_type=site.captcha_type,
                    scraper=site.scraper,
                    needs_js=site.needs_js)


@router.get("/", response_model=list[SiteRead])
def list_sites(db: Session = Depends(get_db), _admin=Depends(get_current_admin_user)):
    sites = db.query(Site).all()
    result = []
    for site in sites:
        links = [l.url for l in site.links]
        result.append(
            SiteRead(
                id=site.id,
                links=links,
                auth_type=site.auth_type,
                captcha_type=site.captcha_type,
                scraper=site.scraper,
                needs_js=site.needs_js,
            )
        )
    return result

@router.post("/{site_id}/run", response_model=TaskResponse, tags=["Sites"])
def run_scraper_now(
    site_id: int,
    db: Session = Depends(deps.get_db),
    _user = Depends(deps.get_current_user),       # mantém rota protegida
):
    site = db.get(models.Site, site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    async_res = celery_app.send_task("scrape_site", args=[site_id])
    return TaskResponse(task_id=async_res.id, status=async_res.state)


@router.get("/tasks/{task_id}", response_model=TaskStatus, tags=["Sites"])
def task_status(task_id: str):
    res = AsyncResult(task_id, app=celery_app)
    return TaskStatus(task_id=task_id,
                      status=res.state,
                      result=res.result if res.state == "SUCCESS" else res.info)

