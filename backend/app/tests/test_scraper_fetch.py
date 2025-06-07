import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scrapers.base import BaseScraper, renew_tor_circuit
from scrapers.config import ScraperConfig, BypassConfig, TorOptions, ExecutionOptions
import requests
from unittest import mock

class DummyScraper(BaseScraper):
    slug = "dummy"
    def parse(self, html: str):
        return []


def test_fetch_onion_retry_and_renew(monkeypatch):
    cfg = ScraperConfig(
        site_id=1,
        type="forum",
        url="http://abc.onion",
        bypass_config=BypassConfig(use_proxies=False, rotate_user_agent=False),
        credentials=None,
        tor=TorOptions(max_retries=1, retry_interval=0),
        execution_options=ExecutionOptions(max_retries=1, timeout_seconds=1),
    )
    scraper = DummyScraper()

    session = requests.Session()
    resp = requests.Response()
    resp.status_code = 200
    resp._content = b"<html>ok</html>"
    get_mock = mock.Mock(side_effect=[requests.Timeout(), resp])
    monkeypatch.setattr(session, "get", get_mock)
    monkeypatch.setattr(scraper, "_build_session", lambda config: session)
    renew_mock = mock.Mock()
    monkeypatch.setattr("scrapers.base.renew_tor_circuit", renew_mock)

    html = scraper.fetch(cfg)
    assert "ok" in html
    assert renew_mock.called
    assert get_mock.call_count == 2
