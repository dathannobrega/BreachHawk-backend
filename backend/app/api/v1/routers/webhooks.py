# api/v1/routers/webhooks.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.v1.deps import get_db, get_current_user
from schemas.webhook import WebhookCreate, WebhookRead
from db.models.webhook import Webhook

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.post("/", response_model=WebhookRead)
def add_webhook(data: WebhookCreate, db: Session = Depends(get_db), user = Depends(get_current_user)):
    hook = Webhook(user_id=user.id, url=data.url)
    db.add(hook); db.commit(); db.refresh(hook)
    return hook

@router.get("/", response_model=list[WebhookRead])
def list_webhooks(db: Session = Depends(get_db), user = Depends(get_current_user)):
    return db.query(Webhook).filter_by(user_id=user.id).all()

@router.delete("/{hook_id}")
def delete_webhook(hook_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    hook = db.query(Webhook).filter_by(id=hook_id, user_id=user.id).first()
    if not hook:
        raise HTTPException(404, "Webhook não encontrado")
    db.delete(hook); db.commit()
    return {"msg": "removido"}
