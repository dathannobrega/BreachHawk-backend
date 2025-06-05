# backend/app/services/email_service.py

from email.message import EmailMessage
from aiosmtplib import send
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from core.config import settings
from core.token_utils import generate_unsubscribe_token
from db.models.smtp_config import SMTPConfig

SMTP_HOST = settings.SMTP_HOST
SMTP_PORT = settings.SMTP_PORT
SMTP_USER = settings.SMTP_USER
SMTP_PASS = settings.SMTP_PASS


def _load_config(db: Session | None = None):
    if db:
        cfg = db.query(SMTPConfig).first()
        if cfg:
            return cfg.host, cfg.port, cfg.username, cfg.password, cfg.from_email
    return SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_USER


async def _send_email(msg: EmailMessage, db: Session | None = None):
    host, port, user, password, from_email = _load_config(db)
    if not msg.get("From"):
        msg["From"] = from_email
    await send(
        msg,
        hostname=host,
        port=port,
        username=user,
        password=password,
        start_tls=True,
    )


async def send_simple_email(to_email: str, subject: str, body: str, db: Session | None = None):
    msg = EmailMessage()
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)
    await _send_email(msg, db)

# Instância global do Jinja2Templates, apontando para a pasta raiz dos seus templates.
# (Certifique-se de que exista uma pasta "./templates/emails/" conforme explicado anteriormente.)
templates = Jinja2Templates(directory="./templates")


async def render_template_to_string(template_name: str, context: dict) -> str:
    """
    Carrega um template Jinja2 e retorna o HTML renderizado como string.
    """
    return templates.env.get_template(template_name).render(**context)


async def send_alert_email(to_email: str, leak: dict, db: Session | None = None):
    """
    Envia e-mail de alerta sobre vazamento (utilizado em outros pontos do sistema).
    Se você já tiver um template HTML específico, basta adaptar este exemplo.
    """
    msg = EmailMessage()
    msg["To"] = to_email
    msg["Subject"] = f"Novo vazamento: {leak['company']}"

    html_template = render_template_to_string(
        "emails/alert_leak.html",
        {
            "subject": msg["Subject"],
            "user_name": leak.get("user_name", to_email),  # ex.: nome do destinatário
            "company_name": leak["company"],
            "country": leak["country"],
            "leak_date": leak["date"],
            "description": leak["description"],
            "leak_url": leak["link"],
            "unsubscribe_url": "https://yourdomain.com/unsubscribe",
        },
    )
    # Como render_template_to_string é async, precisamos aguardá-lo
    html_content = await html_template

    text_content = (
        f"Vazamento detectado: {leak['company']}\n\n"
        f"País: {leak['country']}\n"
        f"Data: {leak['date']}\n"
        f"Descrição: {leak['description']}\n"
        f"Link: {leak['link']}\n\n"
        "Se você já tomou providências, desconsidere esta mensagem."
    )

    msg.set_content(text_content)
    msg.add_alternative(html_content, subtype="html")

    await _send_email(msg, db)


async def send_password_reset_email(to_email: str, reset_link: str, user_name: str, db: Session | None = None):
    """
    Envia e-mail de redefinição de senha.
    - to_email: e-mail do destinatário
    - reset_link: link gerado para resetar senha
    - user_name: nome do usuário, para saudação personalizada
    """
    subject = "Redefinição de senha – Deep Protexion"

    # Renderiza o HTML via Jinja2
    html_content = await render_template_to_string(
        "emails/password_reset.html",
        {
            "subject": subject,
            "user_name": user_name,
            "reset_link": reset_link,
            "unsubscribe_url": "https://yourdomain.com/unsubscribe",
        },
    )

    # Fallback em texto plano (caso o cliente não renderize HTML)
    text_content = (
        f"Olá, {user_name}!\n\n"
        "Você solicitou a redefinição de senha. Clique no link abaixo para criar uma nova senha:\n\n"
        f"{reset_link}\n\n"
        "Se você não solicitou isso, por favor ignore este e-mail.\n"
    )

    msg = EmailMessage()
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(text_content)
    msg.add_alternative(html_content, subtype="html")

    await _send_email(msg, db)




async def send_newsletter_email(to_email: str, user_name: str, db: Session | None = None):
    """Envia uma newsletter de exemplo."""
    user_id = ...  # id do usuário destino
    token = generate_unsubscribe_token(user_id)
    unsubscribe_link = f"{settings.FRONTEND_URL}/unsubscribe?token={token}"

    subject = "Nossa Newsletter Semanal"
    text_content = "Veja as novidades da semana"

    html_content = await render_template_to_string(
        "emails/newsletter.html",
        {
            "subject": subject,
            "user_name": user_name,
            "preheader_text": "Confira as principais novidades desta semana!",
            "body_text": "Aqui vai o texto principal da newsletter...",
            "image_url": "https://yourdomain.com/static/banner.jpg",
            "image_alt": "Banner da Semana",
            "cta_url": "https://yourdomain.com/alguma-promo",
            "cta_label": "Confira Agora",
            "unsubscribe_url": unsubscribe_link,
        },
    )

    msg = EmailMessage()
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(text_content)
    msg.add_alternative(html_content, subtype="html")
    await _send_email(msg, db)


