import pytest
import pytest_asyncio
from email.message import EmailMessage
from aiosmtplib import SMTP
from services.email_service import send_alert_email, send_password_reset_email
from core.config import settings

@pytest.mark.asyncio
async def test_smtp_connection():
    """
    Verifica se o servidor SMTP está alcançável e aceita login.
    """
    smtp = SMTP(
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        start_tls=True,
    )
    await smtp.connect()
    try:
        # tenta autenticar com as credenciais do .env
        await smtp.login(settings.SMTP_USER, settings.SMTP_PASS)
    finally:
        await smtp.quit()

@pytest.mark.asyncio
async def test_send_alert_email_integration():
    """
    Envia um e-mail de alerta real para o próprio remetente (SMTP_USER).
    Verifique sua caixa de entrada para confirmar.
    """
    leak = {
        "company": "IntegrationTestCo",
        "source_url": "http://example.com/leak/123",
        "found_at": "2025-05-07T15:00:00Z",
    }
    # se não lançar exceção, consideramos sucesso
    await send_alert_email(settings.SMTP_USER, leak)

def test_send_password_reset_email_integration():
    """
    Envia um e-mail de redefinição de senha real para o próprio remetente.
    """
    # a função não é async, mas retorna um coroutine daiosmtplib se for necessário await
    result = send_password_reset_email(settings.SMTP_USER, "http://reset-link")
    # se retornar coroutine, executamos
    if hasattr(result, "__await__"):
        import asyncio
        asyncio.get_event_loop().run_until_complete(result)
