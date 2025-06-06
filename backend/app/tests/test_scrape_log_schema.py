from datetime import datetime
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from schemas.scrape_log import ScrapeLogRead


def test_scrape_log_read_instantiation():
    data = {
        "id": 1,
        "site_id": 2,
        "url": "http://example.com",
        "success": True,
        "message": None,
        "created_at": datetime.utcnow(),
    }
    log = ScrapeLogRead(**data)
    assert log.id == 1
    assert log.url == "http://example.com"
