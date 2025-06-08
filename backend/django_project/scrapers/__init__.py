"""Scraper package registering built-in plugins."""

from .base import registry  # noqa: F401

# Import plugins for side effects (they register themselves)
from .ransomhouse import RansomHouseScraper  # noqa: F401
from .telegram import TelegramScraper  # noqa: F401
from .akira_cli import AkiraCLIScraper  # noqa: F401
from .playnews import PlayNewsScraper  # noqa: F401

# Load custom scrapers uploaded at runtime
import importlib.util
import os
import sys

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
