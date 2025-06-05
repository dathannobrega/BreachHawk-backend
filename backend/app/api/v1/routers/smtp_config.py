from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.v1.deps import get_db, get_current_platform_admin_user
from db.models.smtp_config import SMTPConfig
from schemas.smtp_config import SMTPConfigRead, SMTPConfigUpdate, TestEmailRequest
from services.email_service import send_simple_email

router = APIRouter(prefix="/smtp-config", tags=["smtp"])


def _get_current(db: Session) -> SMTPConfig | None:
    return db.query(SMTPConfig).first()


@router.get("/", response_model=SMTPConfigRead)
def read_config(db: Session = Depends(get_db), _=Depends(get_current_platform_admin_user)):
    cfg = _get_current(db)
    if cfg:
        return cfg
    return SMTPConfigRead(host="", port=587, username="", from_email="")


@router.put("/", response_model=SMTPConfigRead)
def update_config(data: SMTPConfigUpdate, db: Session = Depends(get_db), _=Depends(get_current_platform_admin_user)):
    cfg = _get_current(db)
    if cfg:
        cfg.host = data.host
        cfg.port = data.port
        cfg.username = data.username
        cfg.password = data.password
        cfg.from_email = data.from_email
    else:
        cfg = SMTPConfig(**data.model_dump())
        db.add(cfg)
    db.commit()
    db.refresh(cfg)
    return cfg


@router.post("/test")
async def send_test_email(data: TestEmailRequest, db: Session = Depends(get_db), _=Depends(get_current_platform_admin_user)):
    try:
        await send_simple_email(data.to_email, "SMTP Test", "This is a test email", db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True}
