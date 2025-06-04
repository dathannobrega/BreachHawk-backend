from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.templating import Jinja2Templates

from api.v1.routers import google_auth, auth, leaks, sites, snapshots, marketing, users, billing
from db.mongodb import init_mongo_indexes
from core.logging_conf import configure_logging
from core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_mongo_indexes()
    yield
    # (Aqui você poderia colocar lógica de shutdown, se precisar)

def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title="BreachHawk API",
        version="1.0.0",
        lifespan=lifespan  # registra o lifespan em vez de on_event
    )

    # Middleware de CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://www.protexion.cloud"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Middleware de Sessão (necessário para request.session)
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        session_cookie="session",
        max_age=60 * 60 * 24 * 30,  # 30 dias, ajuste conforme precisar
    )

    # Inclui os routers
    app.include_router(auth.router,       prefix="/api/v1/auth",  tags=["auth"])
    app.include_router(google_auth.router, prefix="/api/v1/auth",  tags=["auth"])
    app.include_router(leaks.router,      prefix="/api/v1/leaks",  tags=["leaks"])
    app.include_router(sites.router,      prefix="/api/v1/sites",  tags=["sites"])
    app.include_router(snapshots.router,  prefix="/api/v1/snapshots", tags=["snapshots"])
    app.include_router(marketing.router, prefix="/api/v1/marketing", tags=["marketing"])
    app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
    app.include_router(billing.router, prefix="/api/v1", tags=["billing"])


    # Health check
    @app.get("/", tags=["health"])
    async def root():
        return {"message": "UP"}

    return app

# depois de configurar CORS, routers etc.
templates = Jinja2Templates(directory="./templates")  # aponta para a pasta raiz de templates


# instancia a app
app = create_app()
