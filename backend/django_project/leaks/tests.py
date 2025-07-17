import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from .models import Leak
from .serializers import LeakSerializer
from sites.models import Site
from accounts.models import PlatformUser, UserSearchQuota
from leaks.documents import LeakDoc


@pytest.mark.django_db
def test_leak_model_str():
    site = Site.objects.create(name="S", url="http://s.com")
    leak = Leak.objects.create(
        site=site,
        company="ACME",
        source_url="http://e.com",
    )
    assert str(leak) == "ACME - http://e.com"


@pytest.mark.django_db
def test_leak_serializer():
    leak = Leak.objects.create(company="ACME", source_url="http://e.com")
    data = LeakSerializer(leak).data
    assert data["company"] == "ACME"


@pytest.mark.django_db
def test_leak_api_create_and_list():
    client = APIClient()
    url = reverse("leak-list")
    resp = client.post(url, {"company": "X", "source_url": "http://x.com"})
    assert resp.status_code == 201
    resp = client.get(url)
    assert resp.status_code == 200
    assert resp.data[0]["company"] == "X"


@pytest.mark.django_db
def test_leak_search_endpoint_deducts_quota(monkeypatch):
    user = PlatformUser.objects.create_user(
        username="joe", email="j@x.com", password="pass"
    )
    UserSearchQuota.objects.create(user=user, remaining=2)

    def fake_search(query):
        return [
            LeakDoc(site_id=1, company="Acme", source_url="http://x.com")
        ]

    monkeypatch.setattr("leaks.views.search_leaks", fake_search)

    client = APIClient()
    token = client.post(
        reverse("login"), {"username": "joe", "password": "pass"}
    ).data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    resp = client.get(reverse("leak-search"), {"q": "acme"})

    assert resp.status_code == 200
    assert resp.data["results"][0]["company"] == "Acme"
    quota = UserSearchQuota.objects.get(user=user)
    assert quota.remaining == 1
