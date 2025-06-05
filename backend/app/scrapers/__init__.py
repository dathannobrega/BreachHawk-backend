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

# Carrega scrapers enviados via upload
import importlib.util, os, sys

custom_dir = os.path.join(os.path.dirname(__file__), "custom")
if os.path.isdir(custom_dir):
    for fname in os.listdir(custom_dir):
        if fname.endswith(".py"):
            mod_name = f"scrapers.custom.{fname[:-3]}"
            path = os.path.join(custom_dir, fname)
            spec = importlib.util.spec_from_file_location(mod_name, path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = module
            spec.loader.exec_module(module)
