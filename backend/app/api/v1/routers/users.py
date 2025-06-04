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
    if data.username is not None:
        existing = db.query(User).filter(User.username == data.username).first()
        if existing and existing.id != current_user.id:
            raise HTTPException(status_code=400, detail="Username já em uso")
        current_user.username = data.username
    if data.first_name is not None:
        current_user.first_name = data.first_name
    if data.last_name is not None:
        current_user.last_name = data.last_name
    if data.company is not None:
        current_user.company = data.company
    if data.job_title is not None:
        current_user.job_title = data.job_title
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
