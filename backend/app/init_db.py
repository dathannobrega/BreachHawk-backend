import sys
import subprocess
from db.base import Base
from db.session import engine
from db.models import user  # importe seus modelos aqui

def create_schema():
    print("[*] Criando tabelas diretamente com SQLAlchemy...")
    Base.metadata.create_all(bind=engine)

def run_alembic_migration():
    print("[*] Gerando migration via Alembic...")
    subprocess.run(["alembic", "revision", "-m", "auto migration", "--autogenerate"], check=True)

    print("[*] Aplicando migration via Alembic...")
    subprocess.run(["alembic", "upgrade", "head"], check=True)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "migration":
        run_alembic_migration()
    else:
        create_schema()
