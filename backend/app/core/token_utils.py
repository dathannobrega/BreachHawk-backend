# backend/app/core/token_utils.py

from itsdangerous import URLSafeTimedSerializer
from core.config import settings

# Cria um serializer assinado usando a SECRET_KEY da sua aplicação
# (é recomendável usar algo como: settings.SECRET_KEY + settings.SMTP_USER, para separar do JWT normal).
serializer = URLSafeTimedSerializer(
    secret_key=settings.SECRET_KEY,
    salt="unsubscribe-salt",  # permite diferenciar de outros usos do serializer
)

def generate_unsubscribe_token(user_id: int) -> str:
    # Gera um token que carrega o user_id internamente.
    # Pode-se colocar timestamp interno; depois verificaremos com max_age.
    return serializer.dumps({"user_id": user_id})

def verify_unsubscribe_token(token: str, max_age_seconds: int = 60*60*24*7) -> int:
    """
    Tenta recuperar o user_id a partir do token.
    - max_age_seconds: validade em segundos (opcional).
    Retorna o user_id se válido; se inválido ou expirado, lança BadSignature ou SignatureExpired.
    """
    data = serializer.loads(token, max_age=max_age_seconds)
    return data["user_id"]
