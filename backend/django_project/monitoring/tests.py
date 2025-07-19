import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from accounts.models import PlatformUser
from leaks.models import Leak
from .models import MonitoredResource, Alert


@pytest.mark.django_db
def test_resource_creation_triggers_scan(monkeypatch):
    user = PlatformUser.objects.create_user(
        username="u", email="u@x.com", password="p"
    )
    Leak.objects.create(company="Acme Corp", source_url="http://x.com")

    captured = {}

    def fake_send(*args, **kwargs):
        captured["called"] = True

    monkeypatch.setattr(
        "monitoring.services.send_alert_email", fake_send
    )

    client = APIClient()
    token = client.post(
        reverse("login"), {"username": "u", "password": "p"}
    ).data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    resp = client.post(
        reverse("monitoredresource-list"), {"keyword": "acme"}, format="json"
    )

    assert resp.status_code == 201
    assert Alert.objects.filter(user=user).count() == 1
    assert captured.get("called") is True


@pytest.mark.django_db
def test_alert_created_on_new_leak(monkeypatch):
    user = PlatformUser.objects.create_user(
        username="u2", email="u2@x.com", password="p"
    )
    resource = MonitoredResource.objects.create(user=user, keyword="foo")

    captured = {}

    def fake_send(*args, **kwargs):
        captured["called"] = True

    monkeypatch.setattr(
        "monitoring.services.send_alert_email", fake_send
    )

    Leak.objects.create(company="FooBar", source_url="http://f.com")

    assert Alert.objects.filter(user=user, resource=resource).count() == 1
    assert captured.get("called") is True


@pytest.mark.django_db
def test_alert_list_endpoint(auth_client, admin_user):
    resource = MonitoredResource.objects.create(user=admin_user, keyword="bar")
    Leak.objects.create(company="Bar", source_url="http://b.com")
    resp = auth_client.get(reverse("alert-list"))

    assert resp.status_code == 200
    assert resp.data[0]["resource"] == resource.id
