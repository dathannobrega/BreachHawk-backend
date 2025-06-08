#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path


def main():
    """Run administrative tasks."""
    # Carrega as variáveis de ambiente do arquivo .env
    try:
        from dotenv import load_dotenv

        env_path = Path(__file__).resolve().parent / ".env"
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
            print("Variáveis de ambiente carregadas com sucesso do arquivo .env")
        else:
            print("Arquivo .env não encontrado em:", env_path)
    except ImportError:
        print("python-dotenv não está instalado. Execute: pip install python-dotenv")

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "breachhawk.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
