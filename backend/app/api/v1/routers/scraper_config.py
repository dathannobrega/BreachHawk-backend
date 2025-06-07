from typing import Dict
from fastapi import APIRouter, HTTPException
from scrapers.config import ScraperConfig

router = APIRouter(prefix="/scraper-configs", tags=["scraper-configs"])

_configs: Dict[int, ScraperConfig] = {}

@router.get("/", response_model=list[ScraperConfig])
def list_configs():
    return list(_configs.values())

@router.get("/{site_id}", response_model=ScraperConfig)
def get_config(site_id: int):
    cfg = _configs.get(site_id)
    if not cfg:
        raise HTTPException(status_code=404, detail="config not found")
    return cfg

@router.put("/{site_id}", response_model=ScraperConfig)
def update_config(site_id: int, data: ScraperConfig):
    _configs[site_id] = data
    return data

@router.delete("/{site_id}", status_code=204)
def delete_config(site_id: int):
    _configs.pop(site_id, None)
    return None
