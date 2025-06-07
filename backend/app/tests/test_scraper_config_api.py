import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi.testclient import TestClient
from main import app
from scrapers.config import ScraperConfig, BypassConfig, TorOptions, ExecutionOptions

client = TestClient(app)

cfg = {
    "site_id": 1,
    "type": "website",
    "url": "http://example.com",
    "bypass_config": {"use_proxies": False, "rotate_user_agent": False},
    "credentials": None,
    "tor": {"max_retries": 1, "retry_interval": 0},
    "execution_options": {"max_retries": 1, "timeout_seconds": 1}
}


def test_scraper_config_crud():
    r = client.put("/api/v1/scraper-configs/1", json=cfg)
    assert r.status_code == 200
    r = client.get("/api/v1/scraper-configs/1")
    assert r.json()["url"] == "http://example.com"
    r = client.get("/api/v1/scraper-configs")
    assert len(r.json()) >= 1
    r = client.delete("/api/v1/scraper-configs/1")
    assert r.status_code == 204
