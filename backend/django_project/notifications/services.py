from dataclasses import dataclass

from accounts.models import PlatformUser
from core.token_utils import verify_unsubscribe_token
from django.core.signing import BadSignature, SignatureExpired


@dataclass
class UnsubscribeResult:
    message: str
    status: int


class UnsubscribeError(Exception):
    """Raised when the token is invalid or user does not exist."""


def unsubscribe_user_by_token(token: str) -> UnsubscribeResult:
    """Return an ``UnsubscribeResult`` for the given token."""
    if not token:
        raise UnsubscribeError("Token ausente ou inválido.")
    try:
        user_id = verify_unsubscribe_token(token)
    except SignatureExpired as exc:
        raise UnsubscribeError(
            "Link expirado para cancelamento de inscrição."
        ) from exc
    except BadSignature as exc:
        raise UnsubscribeError(
            "Link inválido. Não foi possível cancelar a inscrição."
        ) from exc

    try:
        user = PlatformUser.objects.get(id=user_id)
    except PlatformUser.DoesNotExist as exc:
        raise UnsubscribeError("Usuário não encontrado.") from exc

    if not user.is_subscribed:
        return UnsubscribeResult(
            "Você já está cancelado. Não receberá mais nossos e-mails.", 200
        )

    user.is_subscribed = False
    user.save(update_fields=["is_subscribed"])
    return UnsubscribeResult(
        "Inscrição cancelada com sucesso!", 200
    )
