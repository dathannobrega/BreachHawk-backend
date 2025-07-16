from stem import Signal
from stem.control import Controller
from django.conf import settings
from ipaddress import ip_address
import socket


def renew_tor_circuit() -> None:
    """Request a new TOR circuit using the control port."""
    host = settings.TOR_CONTROL_HOST
    try:
        ip_address(host)
    except ValueError:
        host = socket.gethostbyname(host)
    with Controller.from_port(address=host, port=settings.TOR_CONTROL_PORT) as ctrl:
        if settings.TOR_CONTROL_PASSWORD:
            ctrl.authenticate(password=settings.TOR_CONTROL_PASSWORD)
        else:
            ctrl.authenticate()
        ctrl.signal(Signal.NEWNYM)
