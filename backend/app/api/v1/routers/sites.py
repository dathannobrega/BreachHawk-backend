from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas.site import SiteCreate, SiteRead
from db import models
from api.v1 import deps
from celery.result import AsyncResult
from celery_app import celery_app
from schemas.task import TaskResponse, TaskStatus
from db.models import Site
from api.v1.deps import get_db

from api.v1.deps import get_current_admin_user

router = APIRouter()

@router.post("/", response_model=SiteRead, status_code=201)
def create_site(site_in: SiteCreate, db: Session = Depends(get_db), _admin=Depends(get_current_admin_user)):

    if db.query(Site).filter(Site.url == site_in.url).first():
        raise HTTPException(400, "Site já existe")

    data = site_in.model_dump()
    site = Site(**data)

    db.add(site)
    db.commit()
    db.refresh(site)
    return site

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

