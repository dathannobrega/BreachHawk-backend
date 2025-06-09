from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string

from .models import SMTPConfig


def _load_config():
    cfg = SMTPConfig.objects.first()
    if cfg:
        return cfg.host, cfg.port, cfg.username, cfg.password, cfg.from_email
    return (
        settings.SMTP_HOST,
        settings.SMTP_PORT,
        settings.SMTP_USER,
        settings.SMTP_PASS,
        settings.SMTP_USER,
    )


def _send_email(subject: str, body: str, html: str | None, to_email: str) -> None:
    host, port, user, password, from_email = _load_config()
    connection = get_connection(
        host=host,
        port=port,
        username=user,
        password=password,
        use_tls=True,
    )
    msg = EmailMultiAlternatives(
        subject, body, from_email, [to_email], connection=connection
    )
    if html:
        msg.attach_alternative(html, "text/html")
    msg.send()


def send_simple_email(to_email: str, subject: str, body: str) -> None:
    _send_email(subject, body, None, to_email)


def send_alert_email(to_email: str, leak: dict) -> None:
    subject = f"Novo vazamento: {leak['company']}"
    html_content = render_to_string(
        "emails/alert_leak.html",
        {
            "subject": subject,
            "user_name": leak.get("user_name", to_email),
            "company_name": leak["company"],
            "country": leak["country"],
            "leak_date": leak["date"],
            "description": leak["description"],
            "leak_url": leak["link"],
            "unsubscribe_url": "https://yourdomain.com/unsubscribe",
        },
    )
    text_content = (
        f"Vazamento detectado: {leak['company']}\n\n"
        f"Pa\u00eds: {leak['country']}\n"
        f"Data: {leak['date']}\n"
        f"Descri\u00e7\u00e3o: {leak['description']}\n"
        f"Link: {leak['link']}\n\n"
        "Se voc\u00ea j\u00e1 tomou provid\u00eancias, desconsidere esta mensagem."
    )
    _send_email(subject, text_content, html_content, to_email)


def send_password_reset_email(to_email: str, reset_link: str, user_name: str) -> None:
    subject = "Redefini\u00e7\u00e3o de senha – Deep Protexion"
    html_content = render_to_string(
        "emails/password_reset.html",
        {
            "subject": subject,
            "user_name": user_name,
            "reset_link": reset_link,
            "unsubscribe_url": "https://yourdomain.com/unsubscribe",
        },
    )
    text_content = (
        f"Ol\u00e1, {user_name}!\n\n"
        "Voc\u00ea solicitou a redefini\u00e7\u00e3o de senha. "
        "Clique no link abaixo para criar uma nova senha:\n\n"
        f"{reset_link}\n\n"
        "Se voc\u00ea n\u00e3o solicitou isso, por favor ignore este e-mail.\n"
    )
    _send_email(subject, text_content, html_content, to_email)


def send_newsletter_email(to_email: str, user_name: str) -> None:
    user_id = 0
    from core.token_utils import generate_unsubscribe_token
    token = generate_unsubscribe_token(user_id)
    unsubscribe_link = f"{settings.FRONTEND_URL}/unsubscribe?token={token}"

    subject = "Nossa Newsletter Semanal"
    text_content = "Veja as novidades da semana"
    html_content = render_to_string(
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
    _send_email(subject, text_content, html_content, to_email)
