from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.auth import UserLogin, Token
from services.auth_service import authenticate_user
from core.jwt import create_access_token
from api.v1.deps import get_db
from core.security import get_password_hash
from schemas.auth import UserCreate, UserOut
from db.models.user import User
from api.v1.deps import get_current_user
from schemas.auth import PasswordChange
from db.models.password_reset import PasswordResetToken
from schemas.password_reset import ForgotPasswordRequest, ResetPasswordRequest
from core.security import verify_password
import secrets
from datetime import datetime, timedelta
from services.email_service import send_password_reset_email
router = APIRouter()

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_in.email, user_in.password)
    if not user:
        raise HTTPException(status_code=400, detail="Credenciais inválidas")

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Usuário já existe")

    hashed_password = get_password_hash(user_in.password)
    user = User(email=user_in.email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/change-password")
def change_password(pwd: PasswordChange, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not verify_password(pwd.old_password, current_user.hashed_password):
        raise HTTPException(400, "Senha atual incorreta")

    current_user.hashed_password = get_password_hash(pwd.new_password)
    db.commit()
    return {"message": "Senha alterada com sucesso"}


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=data.email).first()

    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=1)

    reset_token = PasswordResetToken(user_id=user.id, token=token, expires_at=expires_at)
    db.add(reset_token)
    db.commit()

    reset_link = f"http://localhost:3000/reset-password?token={token}"
    send_password_reset_email(user.email, reset_link)
    return {"message": "Se o e-mail estiver cadastrado, você receberá instruções para redefinir a senha."}

@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    token = db.query(PasswordResetToken).filter_by(token=data.token).first()
    if not token or token.expires_at < datetime.utcnow():
        raise HTTPException(400, "Token inválido ou expirado")

    user = db.query(User).filter_by(id=token.user_id).first()
    if not user:
        raise HTTPException(404, "Usuário não encontrado")

    user.hashed_password = get_password_hash(data.new_password)
    db.delete(token)  # token só pode ser usado uma vez
    db.commit()

    return {"message": "Senha redefinida com sucesso!"}
