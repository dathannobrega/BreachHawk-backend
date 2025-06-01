# api/v1/routers/google_auth.py

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from sqlalchemy.orm import Session
from api.v1.deps import get_db
from core.jwt import create_access_token
from db.models.user import User
import os

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
    redirect_uri = request.url_for('auth_google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth/callback/google", name="auth_google_callback")
async def auth_google_callback(request: Request, db: Session = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    userinfo = token.get("userinfo")

    if not userinfo:
        raise HTTPException(401, detail="Erro ao autenticar com Google")

    user = db.query(User).filter_by(email=userinfo["email"]).first()
    if not user:
        user = User(email=userinfo["email"], hashed_password="!", is_admin=False)
        db.add(user)
        db.commit()
        db.refresh(user)

    jwt = create_access_token({"sub": user.email})
    redirect_url = f"/login?token={jwt}"
    return RedirectResponse(url=redirect_url)
