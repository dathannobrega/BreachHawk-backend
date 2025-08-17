import pytest
from django.urls import reverse
from datetime import datetime, timezone

from .models import ScrapeLog, Snapshot
from .serializers import ScrapeLogSerializer, SnapshotSerializer
from sites.models import Site, TelegramAccount, SiteMetrics
from leaks.documents import LeakDoc
from monitoring.models import Alert, MonitoredResource
from scrapers import service
from accounts.models import PlatformUser



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


@pytest.mark.django_db
def test_run_scraper_produces_alert(monkeypatch):
    """Running a scraper should create alerts for matching keywords."""

    class DummyScraper:
        last_retries = 0

        def run(self, config):
            return [
                LeakDoc(
                    site_id=config.site_id,
                    company="Acme Corp",
                    source_url="http://ex.com",
                    information="important data",
                )
            ]

    # Stub MongoDB interactions
    inserted = []

    class Coll:
        def insert_one(self, data):
            inserted.append(data)
            return type("R", (), {"inserted_id": "1"})()

    class DB:
        leaks = Coll()

    monkeypatch.setattr("leaks.mongo_utils.mongo_db", DB())
    monkeypatch.setattr("leaks.mongo_utils.INDEXES_INITIALIZED", True)

    # Register dummy scraper
    monkeypatch.setitem(service.registry, "dummy", DummyScraper())

    site = Site.objects.create(
        name="Test",
        url="http://t.com",
        scraper="dummy",
        bypass_config={"use_proxies": False, "rotate_user_agent": False},
    )
    user = PlatformUser.objects.create_user(
        username="u", email="u@x.com", password="p"
    )
    resource = MonitoredResource.objects.create(user=user, keyword="acme")

    captured = {}

    def fake_send(*args, **kwargs):
        captured["called"] = True

    monkeypatch.setattr("monitoring.services.send_alert_email", fake_send)

    service.run_scraper_for_site(site.id)

    assert inserted != []
    assert Alert.objects.filter(user=user, resource=resource).count() == 1
    assert captured.get("called") is True


@pytest.mark.django_db
def test_telegram_scraper_runs(monkeypatch):
    account = TelegramAccount.objects.create(api_id=1, api_hash="h", session_string="s")
    site = Site.objects.create(
        name="Group",
        url="https://t.me/group",
        type=Site.SiteType.TELEGRAM,
        scraper="telegram",
        telegram_account=account,
        bypass_config={"use_proxies": False, "rotate_user_agent": False},
    )

    cfg = service._build_config(site, site.url, None)

    class Msg:
        id = 1
        message = "hello"
        date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        link = "https://t.me/group/1"

    class Entity:
        id = 123
        username = "group"

    class DummyClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

        def is_user_authorized(self):
            return True

        def get_entity(self, url):
            return Entity()

        def iter_messages(self, entity):
            return [Msg()]

    monkeypatch.setattr("scrapers.telegram.TelegramClient", DummyClient)

    from scrapers.telegram import TelegramScraper

    leaks = TelegramScraper().run(cfg)
    assert leaks[0]["site_id"] == site.id
    assert leaks[0]["company"] == site.name
    assert leaks[0]["information"] == "hello"
    assert leaks[0]["source_url"] == "https://t.me/group/1"


@pytest.mark.django_db
def test_telegram_scraper_login_failure(monkeypatch):
    account = TelegramAccount.objects.create(api_id=1, api_hash="h")
    site = Site.objects.create(
        name="Group",
        url="https://t.me/group",
        type=Site.SiteType.TELEGRAM,
        scraper="telegram",
        telegram_account=account,
        bypass_config={"use_proxies": False, "rotate_user_agent": False},
    )

    cfg = service._build_config(site, site.url, None)

    class DummyClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

        def is_user_authorized(self):
            return False

    monkeypatch.setattr("scrapers.telegram.TelegramClient", DummyClient)

    from scrapers.telegram import TelegramScraper

    with pytest.raises(RuntimeError):
        TelegramScraper().run(cfg)
    assert SiteMetrics.objects.filter(site=site).count() == 1
