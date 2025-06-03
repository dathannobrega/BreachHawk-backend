# backend/app/api/v1/routers/marketing.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from itsdangerous import SignatureExpired, BadSignature
from core.token_utils import verify_unsubscribe_token
from api.v1.deps import get_db
from db.models.user import User

router = APIRouter()

@router.get("/unsubscribe", response_class=HTMLResponse, tags=["marketing"])
def unsubscribe(token: str, db: Session = Depends(get_db)):
    """
    - Verifica o token; se válido, marca user.is_subscribed = False.
    - Se inválido/expirado, mostra mensagem de erro.
    """
    try:
        user_id = verify_unsubscribe_token(token)
    except SignatureExpired:
        return HTMLResponse(
            content="<h3>Link expirado para cancelamento de inscrição.</h3>",
            status_code=400
        )
    except BadSignature:
        return HTMLResponse(
            content="<h3>Link inválido. Não foi possível cancelar a inscrição.</h3>",
            status_code=400
        )

    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        return HTMLResponse(
            content="<h3>Usuário não encontrado.</h3>",
            status_code=404
        )

    # Marca como “unsubscribed” (pode já estar assim, mas chamamos de qualquer jeito)
    if not user.is_subscribed:
        # Se já estava cancelado, informamos que já está descadastrado
        return HTMLResponse(
            content="<h3>Você já está cancelado. Não receberá mais nossos e-mails.</h3>",
            status_code=200
        )

    user.is_subscribed = False
    db.commit()

    return HTMLResponse(
        content=(
            "<h3>Inscrição cancelada com sucesso!</h3>"
            "<p>Você não receberá mais nossos e-mails promocionais.</p>"
        ),
        status_code=200
    )
