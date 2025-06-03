from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "BreachHawk"
    POSTGRES_USER: str = "admin"
    POSTGRES_PASSWORD: str = "strongpassword"
    POSTGRES_DB: str = "breach_db"
    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_PORT: str = "5432"
    SECRET_KEY: str = "changeme"  # valor padrão opcional
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"

    #MongoDB
    MONGODB_URI: str = "mongodb://mongo:27017"
    MONGODB_DB: str = "breach_db"
    MONGODB_USER: str = "admin"
    MONGODB_PASS: str = "strongpassword"

    # TOR retry / NEWNYM
    TOR_CONTROL_PORT: int        = 9051
    TOR_CONTROL_PASSWORD: str    = "SUA_SENHA_FORTE"     # se você tiver senha no control port
    TOR_MAX_RETRIES: int         = 3
    TOR_RETRY_INTERVAL: float    = 5.0    # segundos entre tentativas
    TOR_PROXY: str = "socks5://tor:9050"

    SMTP_HOST: str = "smtp.seuservidor.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "avisos@meudominio.com"
    SMTP_PASS: str = "senhaforte123!"

    FRONTEND_URL: str = "http://localhost"


    class Config:
        env_file = ".env"

settings = Settings()
