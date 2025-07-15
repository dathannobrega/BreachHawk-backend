import re

import requests
from django.conf import settings
from typing import Optional
from .models import PasswordPolicy


def _load_policy() -> dict:
    policy = PasswordPolicy.objects.first()
    if policy:
        return {
            "min_length": policy.min_length,
            "require_uppercase": policy.require_uppercase,
            "require_lowercase": policy.require_lowercase,
            "require_numbers": policy.require_numbers,
            "require_symbols": policy.require_symbols,
        }
    return {
        "min_length": settings.PASSWORD_MIN_LENGTH,
        "require_uppercase": settings.PASSWORD_REQUIRE_UPPERCASE,
        "require_lowercase": settings.PASSWORD_REQUIRE_LOWERCASE,
        "require_numbers": settings.PASSWORD_REQUIRE_NUMBERS,
        "require_symbols": settings.PASSWORD_REQUIRE_SYMBOLS,
    }


def validate_password(password: str) -> Optional[str]:
    cfg = _load_policy()
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

def get_location_from_ip(ip: str | None) -> str | None:
    """Returns a human readable location from an IP using ipapi.co"""
    if not ip:
        return None
    try:
        resp = requests.get(f"https://ipapi.co/{ip}/json/", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            city = data.get("city")
            region = data.get("region")
            country = data.get("country_name")
            parts = [p for p in [city, region, country] if p]
            return ", ".join(parts) if parts else None
    except Exception:
        pass
    return None