import requests


def get_location_from_ip(ip: str | None) -> str | None:
    """Returns a human readable location from an IP using ipapi.co"""
    if not ip:
        return None
    try:
        resp = requests.get(f"https://ipapi.co/{ip}/json/", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            city = data.get("city")
            region = data.get("region")
            country = data.get("country_name")
            parts = [p for p in [city, region, country] if p]
            return ", ".join(parts) if parts else None
    except Exception:
        pass
    return None
