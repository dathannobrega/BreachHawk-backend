from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from schemas.site import SiteCreate, SiteRead, SiteUpdate
from db import models
from db.models.site_link import SiteLink
from api.v1 import deps
from celery.result import AsyncResult
from celery_app import celery_app
from schemas.task import TaskResponse, TaskStatus
from db.models import Site
from api.v1.deps import get_db

from api.v1.deps import get_current_admin_user
from scrapers import registry
from db.models.scrape_log import ScrapeLog
from schemas.scrape_log import ScrapeLogRead

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

    filename = file.filename
    if not filename.endswith(".py"):
        filename = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(directory, filename)
    with open(path, "wb") as out_file:
        out_file.write(file.file.read())

    before = set(registry.keys())
    try:
        spec = importlib.util.spec_from_file_location(filename[:-3], path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    except Exception as exc:
        os.remove(path)
        raise HTTPException(status_code=400, detail=str(exc))

    new_slugs = set(registry.keys()) - before
    if not new_slugs:
        os.remove(path)
        raise HTTPException(status_code=400, detail="Scraper inválido")
    slug = next(iter(new_slugs))
    new_path = os.path.join(directory, f"{slug}.py")
    if path != new_path:
        os.rename(path, new_path)
    return {"msg": "scraper uploaded", "slug": slug}


@router.get("/scrapers", response_model=list[str], tags=["Sites"])
def list_scrapers(_admin=Depends(get_current_admin_user)):
    return list(registry.keys())


@router.delete("/scrapers/{slug}", status_code=status.HTTP_204_NO_CONTENT, tags=["Sites"])
def delete_scraper(slug: str, _admin=Depends(get_current_admin_user)):
    import os
    custom_dir = "app/scrapers/custom"
    path = os.path.join(custom_dir, f"{slug}.py")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Scraper not found")
    os.remove(path)
    registry.pop(slug, None)
    return None

@router.post("/", response_model=SiteRead, status_code=201)
def create_site(site_in: SiteCreate, db: Session = Depends(get_db), _admin=Depends(get_current_admin_user)):

    # Verifica se algum dos links já está cadastrado
    if db.query(SiteLink).filter(SiteLink.url.in_(site_in.links)).first():
        raise HTTPException(400, "Link já cadastrado")

    if site_in.scraper not in registry:
        raise HTTPException(400, "Scraper desconhecido")

    data = {
        "name": site_in.name,
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
    return SiteRead(id=site.id, name=site.name, links=site_links,
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
                name=site.name,
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


@router.get("/{site_id}/logs", response_model=list[ScrapeLogRead])
def list_scrape_logs(
    site_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin_user),
):
    logs = (
        db.query(ScrapeLog)
        .filter(ScrapeLog.site_id == site_id)
        .order_by(ScrapeLog.created_at.desc())
        .all()
    )
    return logs


@router.put("/{site_id}", response_model=SiteRead)
def update_site(
    site_id: int,
    data: SiteUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin_user),
):
    site = db.get(Site, site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        if field == "links":
            # update links by replacing existing ones
            db.query(SiteLink).filter(SiteLink.site_id == site_id).delete()
            for link in value:
                db.add(SiteLink(site_id=site_id, url=link))
        else:
            setattr(site, field, value)
    db.add(site)
    db.commit(); db.refresh(site)
    links = [l.url for l in site.links]
    return SiteRead(
        id=site.id,
        name=site.name,
        links=links,
        auth_type=site.auth_type,
        captcha_type=site.captcha_type,
        scraper=site.scraper,
        needs_js=site.needs_js,
    )


@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_site(
    site_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin_user),
):
    site = db.get(Site, site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    db.delete(site)
    db.commit()
    return None


@router.post("/{site_id}/urls", response_model=SiteRead)
def add_site_url(
    site_id: int,
    url: str,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin_user),
):
    site = db.get(Site, site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    url = url.rstrip("/")
    if db.query(SiteLink).filter(SiteLink.url == url).first():
        raise HTTPException(status_code=400, detail="Link já cadastrado")
    db.add(SiteLink(site_id=site_id, url=url))
    db.commit(); db.refresh(site)
    links = [l.url for l in site.links]
    return SiteRead(
        id=site.id,
        name=site.name,
        links=links,
        auth_type=site.auth_type,
        captcha_type=site.captcha_type,
        scraper=site.scraper,
        needs_js=site.needs_js,
    )


@router.delete("/urls/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_site_url(
    link_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin_user),
):
    link = db.get(SiteLink, link_id)
    if not link:
        raise HTTPException(status_code=404, detail="URL not found")
    db.delete(link)
    db.commit()
    return None

