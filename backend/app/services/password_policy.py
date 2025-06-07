from sqlalchemy.orm import Session
from core.config import settings
from db.models.password_policy import PasswordPolicy
import re


def _load_policy(db: Session | None) -> dict:
    if db:
        cfg = db.query(PasswordPolicy).first()
        if cfg:
            return {
                "min_length": cfg.min_length,
                "require_uppercase": cfg.require_uppercase,
                "require_lowercase": cfg.require_lowercase,
                "require_numbers": cfg.require_numbers,
                "require_symbols": cfg.require_symbols,
            }
    return {
        "min_length": settings.PASSWORD_MIN_LENGTH,
        "require_uppercase": settings.PASSWORD_REQUIRE_UPPERCASE,
        "require_lowercase": settings.PASSWORD_REQUIRE_LOWERCASE,
        "require_numbers": settings.PASSWORD_REQUIRE_NUMBERS,
        "require_symbols": settings.PASSWORD_REQUIRE_SYMBOLS,
    }


def validate_password(password: str, db: Session | None = None) -> str | None:
    cfg = _load_policy(db)
    if len(password) < cfg["min_length"]:
        return f"Senha deve ter ao menos {cfg['min_length']} caracteres"
    if cfg["require_uppercase"] and not re.search(r"[A-Z]", password):
        return "Senha deve conter letra maiúscula"
    if cfg["require_lowercase"] and not re.search(r"[a-z]", password):
        return "Senha deve conter letra minúscula"
    if cfg["require_numbers"] and not re.search(r"\d", password):
        return "Senha deve conter número"
    if cfg["require_symbols"] and not re.search(r"[^A-Za-z0-9]", password):
        return "Senha deve conter símbolo"
    return None
