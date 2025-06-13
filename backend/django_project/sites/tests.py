import pytest
from django.urls import reverse
from .models import Site, SiteLink, TelegramAccount
from .serializers import SiteSerializer


@pytest.mark.django_db
def test_site_model_str():
    site = Site.objects.create(name="MySite", url="http://s.com")
    assert str(site) == "MySite"


@pytest.mark.django_db
def test_sitelink_model_str():
    site = Site.objects.create(name="MySite", url="http://s.com")
    link = SiteLink.objects.create(site=site, url="http://a.com")
    assert str(link) == "http://a.com"


@pytest.mark.django_db
def test_telegram_account_str():
    acc = TelegramAccount.objects.create(api_id=1, api_hash="h")
    assert str(acc) == f"Account {acc.id}"


@pytest.mark.django_db
def test_site_serializer():
    site = Site.objects.create(name="MySite", url="http://s.com")
    data = SiteSerializer(site).data
    assert data["name"] == "MySite"


@pytest.mark.django_db
def test_site_api_create_list(auth_client):
    url = reverse("site-list")
    resp = auth_client.post(url, {"name": "A", "links": []}, format="json")
    assert resp.status_code == 201
    resp = auth_client.get(url)
    assert resp.status_code == 200
    assert resp.data[0]["name"] == "A"
