import pytest
from django.urls import reverse
from .models import SMTPConfig, Webhook
from .serializers import SMTPConfigSerializer


@pytest.mark.django_db
def test_smtpconfig_model_str():
    obj = SMTPConfig.objects.create(
        host="smtp", port=25, username="u", password="p", from_email="a@b.com"
    )
    assert str(obj) == "SMTP smtp:25"


@pytest.mark.django_db
def test_webhook_model_str(admin_user):
    obj = Webhook.objects.create(user=admin_user, url="http://x.com")
    assert str(obj) == "http://x.com"


@pytest.mark.django_db
def test_smtpconfig_serializer():
    obj = SMTPConfig.objects.create(
        host="smtp", port=25, username="u", password="p", from_email="a@b.com"
    )
    data = SMTPConfigSerializer(obj).data
    assert data["host"] == "smtp"


@pytest.mark.django_db
def test_smtpconfig_api_get_update(auth_client):
    SMTPConfig.objects.create(
        id=1,
        host="smtp",
        port=25,
        username="u",
        password="p",
        from_email="a@b.com",
    )
    url = reverse("smtp-config")
    resp = auth_client.get(url)
    assert resp.status_code == 200
    resp = auth_client.put(
        url,
        {
            "host": "mail",
            "port": 587,
            "username": "u",
            "from_email": "a@b.com",
        },
        format="json",
    )
    assert resp.status_code == 200
    assert resp.data["host"] == "mail"


@pytest.mark.django_db
def test_smtp_test_email_endpoint(auth_client, monkeypatch):
    """Ensure the SMTP test email endpoint sends an email."""

    captured = {}

    def fake_send(to_email: str) -> None:
        captured["arg"] = to_email

    monkeypatch.setattr("notifications.views.send_test_email", fake_send)

    url = reverse("smtp-test")
    resp = auth_client.post(url, {"to_email": "t@example.com"}, format="json")

    assert resp.status_code == 200
    assert resp.data["success"] is True
    assert captured["arg"] == "t@example.com"
