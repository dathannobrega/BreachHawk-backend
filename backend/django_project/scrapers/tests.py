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


@pytest.mark.django_db
def test_upload_list_delete_scraper(auth_client, tmp_path):
    script = tmp_path / "dummy.py"
    script.write_text(
        "from scrapers.base import BaseScraper\n"
        "class Dummy(BaseScraper):\n"
        "    slug='dummy'\n"
        "    def parse(self, html):\n"
        "        return []\n"
    )
    with script.open("rb") as f:
        resp = auth_client.post(
            reverse("scraper-upload"),
            {"file": f},
            format="multipart",
        )
    assert resp.status_code == 201
    assert resp.data["slug"] == "dummy"

    resp = auth_client.get(reverse("scraper-list"))
    assert resp.status_code == 200
    assert "dummy" in resp.data

    resp = auth_client.delete(reverse("scraper-delete", args=["dummy"]))
    assert resp.status_code == 204


@pytest.mark.django_db
def test_run_scraper_endpoint(auth_client, monkeypatch):
    site = Site.objects.create(name="S", url="http://s.com")

    class DummyRes:
        id = "abc"
        state = "PENDING"

    captured = {}

    def fake_schedule(site_id):
        captured["id"] = site_id
        return DummyRes()

    monkeypatch.setattr("scrapers.views.schedule_scraper", fake_schedule)

    url = reverse("scraper-run", args=[site.id])
    resp = auth_client.post(url)

    assert resp.status_code == 202
    assert resp.data["task_id"] == "abc"
    assert captured["id"] == site.id


@pytest.mark.django_db
def test_task_status_endpoint(auth_client, monkeypatch):
    class DummyAsync:
        state = "SUCCESS"
        result = {"inserted": 5}
        info = None

    def fake_async_result(task_id, app=None):
        return DummyAsync()

    monkeypatch.setattr("scrapers.service.AsyncResult", fake_async_result)

    task_id = "11111111-1111-1111-1111-111111111111"
    url = reverse("scraper-task-status", args=[task_id])
    resp = auth_client.get(url)

    assert resp.status_code == 200
    assert resp.data["status"] == "SUCCESS"
    assert resp.data["result"] == {"inserted": 5}


@pytest.mark.django_db
def test_site_log_list_endpoint(auth_client):
    site1 = Site.objects.create(name="A", url="http://a.com")
    site2 = Site.objects.create(name="B", url="http://b.com")
    ScrapeLog.objects.create(site=site1, url="http://a.com", success=True)
    ScrapeLog.objects.create(site=site2, url="http://b.com", success=False)

    url = reverse("site-log-list", args=[site1.id])
    resp = auth_client.get(url)

    assert resp.status_code == 200
    assert len(resp.data) == 1
