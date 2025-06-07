from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.v1.deps import get_db, get_current_platform_admin_user
from db.models.password_policy import PasswordPolicy
from schemas.password_policy import PasswordPolicyRead, PasswordPolicyUpdate

router = APIRouter(prefix="/password-policy", tags=["password"])


def _get_current(db: Session) -> PasswordPolicy | None:
    return db.query(PasswordPolicy).first()


@router.get("/", response_model=PasswordPolicyRead)
def read_policy(db: Session = Depends(get_db), _=Depends(get_current_platform_admin_user)):
    cfg = _get_current(db)
    if cfg:
        return cfg
    from core.config import settings
    return PasswordPolicyRead(
        min_length=settings.PASSWORD_MIN_LENGTH,
        require_uppercase=settings.PASSWORD_REQUIRE_UPPERCASE,
        require_lowercase=settings.PASSWORD_REQUIRE_LOWERCASE,
        require_numbers=settings.PASSWORD_REQUIRE_NUMBERS,
        require_symbols=settings.PASSWORD_REQUIRE_SYMBOLS,
    )


@router.put("/", response_model=PasswordPolicyRead)
def update_policy(data: PasswordPolicyUpdate, db: Session = Depends(get_db), _=Depends(get_current_platform_admin_user)):
    cfg = _get_current(db)
    if cfg:
        cfg.min_length = data.min_length
        cfg.require_uppercase = data.require_uppercase
        cfg.require_lowercase = data.require_lowercase
        cfg.require_numbers = data.require_numbers
        cfg.require_symbols = data.require_symbols
    else:
        cfg = PasswordPolicy(**data.model_dump())
        db.add(cfg)
    db.commit()
    db.refresh(cfg)
    return cfg
