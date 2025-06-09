from django.http import HttpRequest
from .get_ip import get_client_ip


def test_get_client_ip_from_forwarded_header():
    request = HttpRequest()
    request.META['HTTP_X_FORWARDED_FOR'] = '1.1.1.1, 2.2.2.2'
    assert get_client_ip(request) == '1.1.1.1'


def test_get_client_ip_from_remote_addr():
    request = HttpRequest()
    request.META['REMOTE_ADDR'] = '3.3.3.3'
    assert get_client_ip(request) == '3.3.3.3'
