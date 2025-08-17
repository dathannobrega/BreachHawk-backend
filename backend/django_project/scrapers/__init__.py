"""Scraper package registering built-in plugins."""

from .base import registry  # noqa: F401

# Import plugins for side effects (they register themselves)
from .ransomhouse import RansomHouseScraper  # noqa: F401
from .telegram import TelegramScraper  # noqa: F401
from .akira_cli import AkiraCLIScraper  # noqa: F401
from .playnews import PlayNewsScraper  # noqa: F401

import importlib.util
import os
import sys

custom_dir = os.path.join(os.path.dirname(__file__), "custom")


def load_custom_scrapers() -> None:
    """Load or reload custom scrapers from disk."""
    for slug in list(registry.keys()):
        module = registry[slug].__class__.__module__
        if module.startswith("scrapers.custom."):
            registry.pop(slug)

    if os.path.isdir(custom_dir):
        for fname in os.listdir(custom_dir):
            if fname.endswith(".py"):
                mod_name = f"scrapers.custom.{fname[:-3]}"
                path = os.path.join(custom_dir, fname)
                spec = importlib.util.spec_from_file_location(mod_name, path)
                module = importlib.util.module_from_spec(spec)
                sys.modules[mod_name] = module
                spec.loader.exec_module(module)

built_in_dir = os.path.join(os.path.dirname(__file__), "built-in")

def load_built_in_scrapers() -> None:
    if os.path.isdir(built_in_dir):
        for fname in os.listdir(built_in_dir):
            mod_name = f"scrapers.built_in.{fname[:-3]}"
            path = os.path.join(built_in_dir, fname)
            spec = importlib.util.spec_from_file_location(mod_name, path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = module
            spec.loader.exec_module(module)

load_built_in_scrapers()
load_custom_scrapers()
