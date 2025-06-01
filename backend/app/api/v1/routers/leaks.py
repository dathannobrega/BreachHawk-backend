from fastapi import APIRouter, Depends, HTTPException
from repository.leaks_mongo import find_leaks_by_site
from schemas.leak_mongo import LeakDoc
from typing import List

router = APIRouter(prefix="/api/v1/leaks", tags=["leaks"])

@router.get("/", response_model=List[LeakDoc])
async def list_leaks(site_id: int, skip: int = 0, limit: int = 50):
    leaks = await find_leaks_by_site(site_id, skip, limit)
    return leaks
