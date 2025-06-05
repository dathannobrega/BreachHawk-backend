# backend/app/api/v1/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from core.jwt import create_access_token
from core.security import get_password_hash, verify_password
from api.v1.deps import get_db, get_current_user
from services.auth_service import authenticate_user
from services.email_service import send_password_reset_email
from db.models.user import User
from db.models.password_reset import PasswordResetToken
from db.models.login_history import LoginHistory
from db.models.user_session import UserSession
from schemas.auth import UserLogin, UserCreate, UserOut, PasswordChange, AuthResponse
from schemas.password_reset import ForgotPasswordRequest, ResetPasswordRequest

import secrets
from datetime import datetime, timedelta, timezone

router = APIRouter()


@router.post("/login", response_model=AuthResponse, tags=["auth"])
def login(data: UserLogin, db: Session = Depends(get_db)):
    identifier = data.email or data.username
    if not identifier:
        raise HTTPException(status_code=400, detail="Email ou username requerido")
    user = authenticate_user(db, identifier, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    expires = 60 if user.status == "inactive" else None
    access_token = create_access_token({"sub": str(user.id)}, expires_minutes=expires)

    # update last login and record history
    now = datetime.now(timezone.utc)
    user.last_login = now
    db.add(LoginHistory(user_id=user.id, timestamp=now))
    db.add(UserSession(user_id=user.id, token=access_token, expires_at=now + timedelta(minutes=expires or 30)))
    db.commit()
    db.refresh(user)

    return {"access_token": access_token, "token_type": "bearer", "user": user}


@router.post("/register", response_model=AuthResponse, tags=["auth"])
def register(data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(
        (User.email == data.email) | (User.username == data.username)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="E-mail ou usuário já cadastrado")
    new_user = User(
        username=data.username,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        company=data.company,
        job_title=data.job_title,
        role="user",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    access_token = create_access_token({"sub": str(new_user.id)})
    return {"access_token": access_token, "token_type": "bearer", "user": new_user}


@router.post("/forgot-password", tags=["auth"])
async def forgot_password(
    data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Gera token de reset, salva no banco e dispara e-mail de recuperação em background.
    """
    user = db.query(User).filter_by(email=data.email).first()
    if not user:
        # Para não vazar se o e-mail existe ou não, devolvemos 200 mesmo assim
        return {"message": "Se o e-mail estiver cadastrado, você receberá instruções para redefinir a senha."}

    # Gera token aleatório e expira em 1 hora
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    reset_token = PasswordResetToken(
        user_id=user.id,
        token=token,
        expires_at=expires_at,
    )
    db.add(reset_token)
    db.commit()

    reset_link = f"https://dev.protexion.cloud/reset-password?token={token}"
    # Agora passamos também o user.email (ou user.name, se existir um campo de nome no model)
    background_tasks.add_task(send_password_reset_email, user.email, reset_link, user.email)

    return {"message": "Se o e-mail estiver cadastrado, você receberá instruções para redefinir a senha."}


@router.post("/reset-password", tags=["auth"])
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    """
    Verifica o token, redefine a senha e remove o token do DB.
    """
    token_obj = db.query(PasswordResetToken).filter_by(token=data.token).first()
    if not token_obj or token_obj.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")

    user = db.query(User).filter_by(id=token_obj.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    user.hashed_password = get_password_hash(data.new_password)
    db.delete(token_obj)
    db.commit()

    return {"message": "Senha redefinida com sucesso!"}


@router.post("/change-password", tags=["auth"])
def change_password(
    data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Alteração de senha já logado: valida a senha antiga e muda para a nova.
    """
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Senha antiga incorreta")

    current_user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    return {"message": "Senha alterada com sucesso!"}


@router.get("/me", response_model=UserOut, tags=["auth"])
def read_current_user(current_user: User = Depends(get_current_user)):
    """Retorna os dados do usuário autenticado."""
    return current_user


from typing import List
from schemas import LoginHistoryRead, UserSessionRead

@router.get("/login-history", response_model=List[LoginHistoryRead], tags=["auth"])
def get_login_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(LoginHistory).filter_by(user_id=current_user.id).order_by(LoginHistory.timestamp.desc()).all()


@router.get("/sessions", response_model=List[UserSessionRead], tags=["auth"])
def get_sessions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(UserSession).filter_by(user_id=current_user.id).order_by(UserSession.created_at.desc()).all()


@router.delete("/sessions/{session_id}", tags=["auth"])
def delete_session(session_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(UserSession).filter_by(id=session_id, user_id=current_user.id).first()
    if session:
        db.delete(session)
        db.commit()
    return {"success": True}
