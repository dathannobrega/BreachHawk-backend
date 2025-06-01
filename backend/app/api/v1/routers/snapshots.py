# api/v1/routers/snapshots.py
from fastapi import Depends, HTTPException, APIRouter
from fastapi.responses import Response

from api.v1.deps import get_db
from db.models.snapshot import ScrapeSnapshot
from schemas.snapshot import SnapshotRead
from typing import List

router = APIRouter(prefix="/api/v1/snapshots", tags=["snapshots"])

# listar todos os snapshots (com paginação opcional)
@router.get("/", response_model=List[SnapshotRead])
def list_snapshots(skip: int = 0, limit: int = 50, db=Depends(get_db)):
    snaps = db.query(ScrapeSnapshot).offset(skip).limit(limit).all()
    return snaps



@router.get("/{snapshot_id}/png")
def get_png(snapshot_id: int, db=Depends(get_db)):
    snap = db.get(ScrapeSnapshot, snapshot_id)
    if not snap:
        raise HTTPException(404)
    return Response(content=snap.screenshot,
                    media_type="image/png")
