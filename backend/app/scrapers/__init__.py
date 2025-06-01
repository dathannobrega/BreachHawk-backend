"""
Pacote de scrapers: importa a base (cria o registry)
e, em seguida, importa cada plugin para que se registrem.
"""

from .base import registry          # ← use APENAS esta linha ‼

# Remova (ou comente) qualquer linha como:
# registry: dict[str, "ScraperBase"] = {}

# Importes dos plugins apenas para side‑effect
from .akira_cli import AkiraCLIScraper        # noqa: F401
from .ransomhouse import RansomHouseScraper   # noqa: F401
from .playnews import PlayNewsScraper   # noqa: F401
