from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.v1.deps import get_db, get_current_user
from schemas.auth import UserOut, UserUpdate
from db.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserOut)
def update_current_user(
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.profile_image is not None:
        current_user.profile_image = data.profile_image
    if data.organization is not None:
        current_user.organization = data.organization
    if data.contact is not None:
        current_user.contact = data.contact
    if data.is_subscribed is not None:
        current_user.is_subscribed = data.is_subscribed
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
