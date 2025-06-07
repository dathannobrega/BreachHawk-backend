import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scrapers.base import BaseScraper
from scrapers.config import ScraperConfig, BypassConfig, TorOptions, ExecutionOptions
from unittest import mock

class DummyScraper(BaseScraper):
    slug = "dummy_run"
    def parse(self, html: str):
        return ["parsed"]

def test_run_calls_fetch_and_parse(monkeypatch):
    scraper = DummyScraper()
    renew = mock.Mock()
    monkeypatch.setattr("scrapers.base.renew_tor_circuit", renew)
    monkeypatch.setattr(DummyScraper, "fetch", lambda self, cfg: "<html></html>")
    cfg = ScraperConfig(
        site_id=1,
        type="website",
        url="http://test.com",
        bypass_config=BypassConfig(use_proxies=False, rotate_user_agent=False),
        credentials=None,
        tor=TorOptions(max_retries=1, retry_interval=0),
        execution_options=ExecutionOptions(max_retries=1, timeout_seconds=1),
    )
    result = scraper.run(cfg)
    assert result == ["parsed"]
