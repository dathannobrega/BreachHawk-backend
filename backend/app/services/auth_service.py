from sqlalchemy.orm import Session
from db.models.user import User
from core.security import verify_password

def authenticate_user(db: Session, identifier: str, password: str):
    """Authenticate by email or username."""
    user = (
        db.query(User)
        .filter((User.email == identifier) | (User.username == identifier))
        .first()
    )
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
