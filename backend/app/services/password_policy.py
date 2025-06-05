from core.config import settings
import re


def validate_password(password: str) -> str | None:
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        return f"Senha deve ter ao menos {settings.PASSWORD_MIN_LENGTH} caracteres"
    if settings.PASSWORD_REQUIRE_UPPERCASE and not re.search(r"[A-Z]", password):
        return "Senha deve conter letra maiúscula"
    if settings.PASSWORD_REQUIRE_LOWERCASE and not re.search(r"[a-z]", password):
        return "Senha deve conter letra minúscula"
    if settings.PASSWORD_REQUIRE_NUMBERS and not re.search(r"\d", password):
        return "Senha deve conter número"
    if settings.PASSWORD_REQUIRE_SYMBOLS and not re.search(r"[^A-Za-z0-9]", password):
        return "Senha deve conter símbolo"
    return None
