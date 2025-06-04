# api/v1/routers/google_auth.py
from http.client import HTTPException

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from sqlalchemy.orm import Session
from api.v1.deps import get_db
from core.jwt import create_access_token
from db.models.user import User
import os

from core.config import settings

router = APIRouter()
config = Config(".env")

oauth = OAuth(config)
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@router.get("/login/google")
async def login_via_google(request: Request):
    redirect_uri = request.url_for('auth_google_callback').replace(scheme="https")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/callback/google", name="auth_google_callback")
async def auth_google_callback(request: Request, db: Session = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    userinfo = token.get("userinfo")

    if not userinfo:
        raise HTTPException(401, detail="Erro ao autenticar com Google")

    # Cria ou encontra usuário no banco
    user = db.query(User).filter_by(email=userinfo["email"]).first()
    if not user:
        user = User(email=userinfo["email"], hashed_password="!", is_admin=False)
        db.add(user)
        db.commit()
        db.refresh(user)

    # Gera o JWT
    jwt = create_access_token({"sub": str(user.id)})


    # Em vez de apenas "/login?token=...", usamos a URL completa do frontend
    frontend_url = settings.FRONTEND_URL  # ex: "http://localhost:3000"
    if not frontend_url:
        # Em caso de faltar a variável, levanta erro para não redirecionar pra lugar errado
        raise HTTPException(
            500,
            detail="Variável de ambiente FRONTEND_URL não configurada. Não sei para onde redirecionar."
        )

    # Monta a URL final: http://localhost:3000/login?token=eyJ...
    redirect_url = f"{frontend_url}/login?token={jwt}"
    return RedirectResponse(url=redirect_url)
