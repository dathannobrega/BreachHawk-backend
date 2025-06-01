from email.message import EmailMessage
from aiosmtplib import send
from jinja2 import Template
from core.config import settings


SMTP_HOST = settings.SMTP_HOST
SMTP_PORT = settings.SMTP_PORT
SMTP_USER = settings.SMTP_USER
SMTP_PASS = settings.SMTP_PASS

async def send_alert_email(to_email: str, leak: dict):
    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = f"Novo vazamento: {leak['company']}"

    html_template = Template("""
    <h2>Vazamento Detectado</h2>
    <p><strong>Empresa:</strong> {{ company }}</p>
    <p><strong>URL:</strong> <a href="{{ source_url }}">{{ source_url }}</a></p>
    <p><strong>Encontrado em:</strong> {{ found_at }}</p>
    """)
    msg.set_content("Novo vazamento encontrado.")
    msg.add_alternative(html_template.render(**leak), subtype="html")

    await send(msg, hostname=SMTP_HOST, port=SMTP_PORT,
               username=SMTP_USER, password=SMTP_PASS, start_tls=True)

def send_password_reset_email(to_email: str, reset_link: str):
    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = "Redefinição de senha – Deep Protexion"

    msg.set_content(f"""
    Olá!

    Foi solicitada a redefinição da sua senha. Acesse o link abaixo para criar uma nova senha:

    {reset_link}

    Se você não solicitou isso, ignore este e-mail.
    """)

    send(msg, hostname=SMTP_HOST, port=SMTP_PORT,
         username=SMTP_USER, password=SMTP_PASS, start_tls=True)
