# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.routers import google_auth, auth, leaks, sites, snapshots
from db.mongodb import init_mongo_indexes
from core.logging_conf import configure_logging

def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title="BreachHawk API",
        version="1.0.0"
    )

    # Middleware de CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Inclui os routers
    app.include_router(auth.router,      prefix="/api/v1/auth",  tags=["auth"])
    app.include_router(google_auth.router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(leaks.router,     prefix="/api/v1/leaks", tags=["leaks"])
    app.include_router(sites.router,     prefix="/api/v1/sites", tags=["sites"])
    app.include_router(snapshots.router, prefix="/api/v1/snapshots", tags=["snapshots"])

    # Health check
    @app.get("/", tags=["health"])
    async def root():
        return {"message": "UP"}

    # Startup: cria índices no Mongo
    @app.on_event("startup")
    async def startup_event():
        await init_mongo_indexes()

    return app

# instancia a app
app = create_app()
