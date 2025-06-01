# app/utils/tor.py

from stem import Signal
from stem.control import Controller
from core.config import settings

def renew_tor_circuit() -> None:
    """
    Envia SIGNAL NEWNYM para o Tor control port,
    forçando um novo circuito.
    """
    with Controller.from_port(port=settings.TOR_CONTROL_PORT) as ctrl:
        # autentique se precisar
        if settings.TOR_CONTROL_PASSWORD:
            ctrl.authenticate(password=settings.TOR_CONTROL_PASSWORD)
        else:
            ctrl.authenticate()
        ctrl.signal(Signal.NEWNYM)
