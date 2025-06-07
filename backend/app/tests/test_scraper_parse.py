import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scrapers.telegram import TelegramScraper
from scrapers.ransomhouse import RansomHouseScraper

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def read_fixture(name):
    with open(os.path.join(FIXTURES, name), "r", encoding="utf-8") as f:
        return f.read()


def test_parse_telegram():
    html = read_fixture("telegram.html")
    scraper = TelegramScraper()
    leaks = scraper.parse(html)
    assert leaks and leaks[0]["information"] == "Hello World"


def test_parse_ransomhouse():
    html = read_fixture("ransomhouse.html")
    scraper = RansomHouseScraper()
    leaks = scraper.parse(html)
    assert leaks and leaks[0]["company"] == "Acme Corp"
