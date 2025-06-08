from stem import Signal
from stem.control import Controller
from django.conf import settings


def renew_tor_circuit() -> None:
    """Request a new TOR circuit using the control port."""
    with Controller.from_port(port=settings.TOR_CONTROL_PORT) as ctrl:
        if settings.TOR_CONTROL_PASSWORD:
            ctrl.authenticate(password=settings.TOR_CONTROL_PASSWORD)
        else:
            ctrl.authenticate()
        ctrl.signal(Signal.NEWNYM)
