from typing import Iterable
from django.db.models import Q
from leaks.models import Leak
from .models import MonitoredResource, Alert
from notifications.email_utils import send_alert_email


MATCH_FIELDS = ["company", "information", "comment"]


def leak_matches_keyword(leak: Leak, keyword: str) -> bool:
    key = keyword.lower()
    for field in MATCH_FIELDS:
        value = getattr(leak, field, "") or ""
        if key in value.lower():
            return True
    return False


def create_alert(user, resource: MonitoredResource, leak: Leak) -> Alert:
    alert, created = Alert.objects.get_or_create(
        user=user, resource=resource, leak=leak
    )
    if created:
        leak_info = {
            "user_name": user.username,
            "company": leak.company,
            "country": leak.country or "",
            "date": leak.found_at,
            "description": leak.information or "",
            "link": leak.source_url,
        }
        try:
            send_alert_email(user.email, leak_info)
        except Exception:
            pass
    return alert


def scan_existing_leaks(resource: MonitoredResource) -> int:
    key = resource.keyword
    query = Q()
    for field in MATCH_FIELDS:
        query |= Q(**{f"{field}__icontains": key})
    leaks = Leak.objects.filter(query)
    count = 0
    for leak in leaks:
        alert = create_alert(resource.user, resource, leak)
        if alert:
            count += 1
    return count


def check_leak_against_resources(leak: Leak) -> None:
    for resource in MonitoredResource.objects.all():
        if leak_matches_keyword(leak, resource.keyword):
            create_alert(resource.user, resource, leak)
