import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from .models import Leak
from .serializers import LeakSerializer
from sites.models import Site

@pytest.mark.django_db
def test_leak_model_str():
    site = Site.objects.create(name="S", url="http://s.com")
    leak = Leak.objects.create(site=site, company="ACME", source_url="http://e.com")
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
