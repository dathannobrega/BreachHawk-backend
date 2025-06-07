from schemas.site import SiteCreate, SiteType, BypassConfig, Credentials


def test_sitecreate_with_nested_objects():
    data = {
        "name": "Forum X",
        "links": ["http://example.onion"],
        "type": "forum",
        "bypassConfig": {"useProxies": True, "rotateUserAgent": True, "captchaSolver": "2captcha"},
        "credentials": {"username": "u", "password": "p"}
    }
    site = SiteCreate(**data)
    assert site.type == SiteType.forum
    assert site.bypassConfig.useProxies is True
    assert site.credentials.username == "u"

