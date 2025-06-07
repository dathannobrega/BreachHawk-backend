# backend/app/api/v1/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.orm import Session
from core.jwt import create_access_token
from core.security import get_password_hash, verify_password
from services.password_policy import validate_password
from core.config import settings
from api.v1.deps import get_db, get_current_user
from services.email_service import send_password_reset_email
from services.geo_service import get_location_from_ip
from db.models.user import User
from db.models.password_reset import PasswordResetToken
from db.models.login_history import LoginHistory
from db.models.user_session import UserSession
from schemas.auth import UserLogin, UserCreate, UserOut, PasswordChange, AuthResponse
from schemas.password_reset import ForgotPasswordRequest, ResetPasswordRequest

import secrets
from datetime import datetime, timedelta, timezone
from utils.get_ip import get_client_ip

router = APIRouter()


@router.post("/login", response_model=AuthResponse, tags=["auth"])
def login(
    data: UserLogin,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Login endpoint. api/v1/auth/login

    - Receives the user's email/username and password.
    - If valid, resets failed login attempts, updates last login and creates a JWT.
    - Returns the token, token type and authenticated user.
    """
    identifier = data.email or data.username
    if not identifier:
        raise HTTPException(status_code=400, detail="Email ou username requerido")
    user = db.query(User).filter((User.email == identifier) | (User.username == identifier)).first()

    client_ip = get_client_ip(request)

    device = request.headers.get("user-agent")
    location = get_location_from_ip(ip)
    now = datetime.now(timezone.utc)
    if not user:
        db.add(LoginHistory(user_id=None, timestamp=now, device=device, ip_address=ip, location=location, success=False))
        db.commit()
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    if user.lockout_until and user.lockout_until > now:
        raise HTTPException(status_code=403, detail="Conta bloqueada")

    if not verify_password(data.password, user.hashed_password):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
            user.lockout_until = now + timedelta(minutes=settings.ACCOUNT_LOCKOUT_MINUTES)
            user.failed_login_attempts = 0
        db.add(LoginHistory(user_id=user.id, timestamp=now, device=device, ip_address=ip, location=location, success=False))
        db.commit()
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    user.failed_login_attempts = 0
    user.lockout_until = None

    expires_minutes = settings.SESSION_TIMEOUT_HOURS * 60
    access_token = create_access_token({"sub": str(user.id)}, expires_minutes=expires_minutes)

    # update last login and record history
    now = datetime.now(timezone.utc)
    user.last_login = now
    db.add(LoginHistory(user_id=user.id, timestamp=now, device=device, ip_address=ip, location=location, success=True))
    db.add(UserSession(user_id=user.id, token=access_token, device=device, ip_address=ip, location=location, expires_at=now + timedelta(minutes=expires_minutes)))
    db.commit()
    db.refresh(user)

    return {"access_token": access_token, "token_type": "bearer", "user": user}


@router.post("/register", response_model=AuthResponse, tags=["auth"])
def register(data: UserCreate, db: Session = Depends(get_db)):
    """
    Registration endpoint. api/v1/auth/register

    - Validates email/username uniqueness.
    - Validates the provided password strength.
    - Creates a new user, generates and returns a JWT.
    """
    existing = db.query(User).filter(
        (User.email == data.email) | (User.username == data.username)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="E-mail ou usuário já cadastrado")
    error = validate_password(data.password, db)
    if error:
        raise HTTPException(status_code=400, detail=error)
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
    exp = settings.SESSION_TIMEOUT_HOURS * 60
    access_token = create_access_token({"sub": str(new_user.id)}, expires_minutes=exp)
    return {"access_token": access_token, "token_type": "bearer", "user": new_user}


@router.post("/forgot-password", tags=["auth"])
async def forgot_password(
    data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Forgot Password endpoint. api/v1/auth/forgot-password

    - Generates a password reset token if the email is registered.
    - Schedules sending a reset email in the background.
    - Always returns a success message to prevent information leakage.
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
    background_tasks.add_task(send_password_reset_email, user.email, reset_link, user.email)

    return {"message": "Se o e-mail estiver cadastrado, você receberá instruções para redefinir a senha."}


@router.post("/reset-password", tags=["auth"])
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    """
    Reset Password endpoint. api/v1/auth/reset-password

    - Validates the reset token and its expiration.
    - Validates the strength of the new password.
    - Updates the user's password and removes the used token.
    """
    token_obj = db.query(PasswordResetToken).filter_by(token=data.token).first()
    if not token_obj or token_obj.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")

    user = db.query(User).filter_by(id=token_obj.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    error = validate_password(data.new_password, db)
    if error:
        raise HTTPException(status_code=400, detail=error)

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
    Change Password endpoint (authenticated users). api/v1/auth/change-password

    - Verifies the old password.
    - Validates and updates the password.
    - Returns a success message on completion.
    """
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Senha antiga incorreta")

    error = validate_password(data.new_password, db)
    if error:
        raise HTTPException(status_code=400, detail=error)

    current_user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    return {"message": "Senha alterada com sucesso!"}


@router.get("/me", response_model=UserOut, tags=["auth"])
def read_current_user(current_user: User = Depends(get_current_user)):
    """
    Get Current User endpoint. api/v1/auth/me

    - Retrieves the authenticated user's profile.
    """
    return current_user


from typing import List
from schemas import LoginHistoryRead, UserSessionRead

@router.get("/login-history", response_model=List[LoginHistoryRead], tags=["auth"])
def get_login_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Login History endpoint. api/v1/auth/login-history

    - Returns a list of login history records for the current user, ordered by most recent.
    """
    return db.query(LoginHistory).filter_by(user_id=current_user.id).order_by(LoginHistory.timestamp.desc()).all()


@router.get("/sessions", response_model=List[UserSessionRead], tags=["auth"])
def get_sessions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get Sessions endpoint. api/v1/auth/sessions

    - Retrieves all active sessions for the authenticated user.
    """
    return db.query(UserSession).filter_by(user_id=current_user.id).order_by(UserSession.created_at.desc()).all()


@router.delete("/sessions/{session_id}", tags=["auth"])
def delete_session(session_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Delete Session endpoint. api/v1/auth/sessions/{session_id}

    - Deletes a specific user session for the current authenticated user.
    - Returns a success confirmation.
    """
    session = db.query(UserSession).filter_by(id=session_id, user_id=current_user.id).first()
    if session:
        db.delete(session)
        db.commit()
    return {"success": True}
