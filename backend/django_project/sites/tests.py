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
    SiteLink.objects.create(site=site, url="http://s.com")
    data = SiteSerializer(site).data
    assert data["name"] == "MySite"
    assert data["url"] == "http://s.com"
    assert data["links"][0]["url"] == "http://s.com"


@pytest.mark.django_db
def test_site_api_create_list(auth_client):
    url = reverse("site-list")
    data = {
        "name": "A",
        "url": "http://example.com",
        "links": [
            {"url": "http://example.com"},
            {"url": "http://b.com"},
        ],
    }
    resp = auth_client.post(url, data, format="json")
    assert resp.status_code == 201
    resp = auth_client.get(url)
    assert resp.status_code == 200
    assert resp.data[0]["name"] == "A"


@pytest.mark.django_db
def test_site_create_without_url(auth_client):
    endpoint = reverse("site-list")
    data = {
        "name": "Akira",
        "links": [{"url": "http://akira.onion"}],
        "type": "website",
        "auth_type": "none",
        "captcha_type": "none",
        "scraper": "akira_cli",
        "needs_js": True,
        "enabled": True,
        "bypass_config": {"use_proxies": True},
    }
    resp = auth_client.post(endpoint, data, format="json")
    assert resp.status_code == 201
    site = Site.objects.get(id=resp.data["id"])
    assert site.url == "http://akira.onion"
    assert site.links.count() == 1


@pytest.mark.django_db
def test_telegram_account_list_endpoint(auth_client):
    TelegramAccount.objects.create(
        api_id=123,
        api_hash="abc",
        phone="+1111111",
    )
    resp = auth_client.get(reverse("telegram-account-list"))
    assert resp.status_code == 200
    assert resp.data[0]["api_id"] == 123


@pytest.mark.django_db
def test_telegram_account_crud(auth_client):
    url = reverse("telegram-account-list")
    data = {
        "api_id": 111,
        "api_hash": "hash",
        "session_string": "sess",
        "phone": "+123",
    }
    create = auth_client.post(url, data, format="json")
    assert create.status_code == 201
    acc_id = create.data["id"]

    detail = reverse("telegram-account-detail", args=[acc_id])
    retrieve = auth_client.get(detail)
    assert retrieve.status_code == 200
    assert retrieve.data["api_id"] == 111

    update_data = {
        "api_id": 222,
        "api_hash": "hash2",
        "session_string": "sess2",
        "phone": "+456",
    }
    update = auth_client.put(detail, update_data, format="json")
    assert update.status_code == 200
    assert update.data["api_id"] == 222

    delete = auth_client.delete(detail)
    assert delete.status_code == 204
    assert TelegramAccount.objects.count() == 0


@pytest.mark.django_db
def test_site_update_preserves_link(auth_client):
    site = Site.objects.create(name="A", url="http://a.com")
    link = SiteLink.objects.create(site=site, url="http://a.com")

    detail = reverse("site-detail", args=[site.id])
    data = {
        "name": "A1",
        "url": "http://a.com",
        "links": [{"id": link.id, "url": "http://a.com"}],
        "type": site.type,
        "auth_type": site.auth_type,
        "captcha_type": site.captcha_type,
        "scraper": site.scraper,
        "needs_js": site.needs_js,
        "enabled": site.enabled,
        "bypass_config": site.bypass_config,
        "credentials": site.credentials,
        "telegram_account": None,
    }

    resp = auth_client.put(detail, data, format="json")
    assert resp.status_code == 200, resp.data
    site.refresh_from_db()
    assert site.name == "A1"
    assert site.links.count() == 1
    assert site.links.first().id == link.id


@pytest.mark.django_db
def test_site_update_change_link_url(auth_client):
    site = Site.objects.create(name="A", url="http://a.com")
    link = SiteLink.objects.create(site=site, url="http://a.com")

    detail = reverse("site-detail", args=[site.id])
    data = {
        "name": "A",  # unchanged
        "url": "http://a.com",
        "links": [{"id": link.id, "url": "http://new.com"}],
        "type": site.type,
        "auth_type": site.auth_type,
        "captcha_type": site.captcha_type,
        "scraper": site.scraper,
        "needs_js": site.needs_js,
        "enabled": site.enabled,
        "bypass_config": site.bypass_config,
        "credentials": site.credentials,
        "telegram_account": None,
    }

    resp = auth_client.put(detail, data, format="json")
    assert resp.status_code == 200, resp.data
    site.refresh_from_db()
    assert site.links.count() == 1
    assert site.links.first().id == link.id
    assert site.links.first().url == "http://new.com"
