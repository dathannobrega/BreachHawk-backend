import pytest
from django.urls import reverse
from .models import ScrapeLog, Snapshot
from .serializers import ScrapeLogSerializer, SnapshotSerializer
from sites.models import Site


@pytest.mark.django_db
def test_scrapelog_model_str():
    site = Site.objects.create(name="S", url="http://s.com")
    log = ScrapeLog.objects.create(site=site, url="http://a.com", success=True)
    assert str(log) == f"{site} - http://a.com"


@pytest.mark.django_db
def test_snapshot_model_str():
    site = Site.objects.create(name="S", url="http://s.com")
    snap = Snapshot.objects.create(site=site)
    assert str(snap) == f"Snapshot {snap.id} for {site}"


@pytest.mark.django_db
def test_serializers():
    site = Site.objects.create(name="S", url="http://s.com")
    log = ScrapeLog.objects.create(site=site, url="http://a.com", success=True)
    snap = Snapshot.objects.create(site=site)
    assert ScrapeLogSerializer(log).data["url"] == "http://a.com"
    assert SnapshotSerializer(snap).data["site"] == site.id


@pytest.mark.django_db
def test_scraper_api_list(auth_client):
    site = Site.objects.create(name="S", url="http://s.com")
    ScrapeLog.objects.create(site=site, url="http://a.com", success=True)
    Snapshot.objects.create(site=site)
    resp = auth_client.get(reverse("scrapelog-list"))
    assert resp.status_code == 200
    assert len(resp.data) == 1
    resp = auth_client.get(reverse("snapshot-list"))
    assert resp.status_code == 200
    assert len(resp.data) == 1
