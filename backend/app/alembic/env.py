from logging.config import fileConfig
from sqlalchemy import pool
from alembic import context
import os

from dotenv import load_dotenv
from db.base import Base  # sua base declarativa
from db.session import engine  # seu engine já configurado
from db.base import Base
from db.models import user, site, leak, snapshot, site_metrics, password_reset

# Carregar variáveis de ambiente do .env
load_dotenv("../../../.env")

# Configurar logging
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Definir a base para autogenerate
target_metadata = Base.metadata

def run_migrations_offline():
    """Rodar migrations em modo offline."""
    url = os.getenv("SQLALCHEMY_DATABASE_URI")  # ou use o mesmo nome que você usa em session.py
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Rodar migrations em modo online."""
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
