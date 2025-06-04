from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.v1.deps import get_db, get_current_platform_admin_user
from schemas.platform_user import PlatformUserCreate, PlatformUserRead, PlatformUserUpdate
from db.models.user import User
from core.security import get_password_hash

router = APIRouter(prefix="/platform-users", tags=["platform_users"])

@router.get("/", response_model=List[PlatformUserRead])
def list_users(db: Session = Depends(get_db), _=Depends(get_current_platform_admin_user)):
    return db.query(User).all()

@router.post("/", response_model=PlatformUserRead, status_code=201)
def create_user(data: PlatformUserCreate, db: Session = Depends(get_db), _=Depends(get_current_platform_admin_user)):
    if db.query(User).filter((User.email == data.email) | (User.username == data.username)).first():
        raise HTTPException(status_code=400, detail="User already exists")
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        role=data.role,
        status=data.status.value,
        company=data.company,
        job_title=data.job_title,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/{user_id}", response_model=PlatformUserRead)
def get_user(user_id: int, db: Session = Depends(get_db), _=Depends(get_current_platform_admin_user)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=PlatformUserRead)
def update_user(user_id: int, data: PlatformUserUpdate, db: Session = Depends(get_db), _=Depends(get_current_platform_admin_user)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    updates = data.model_dump(exclude_unset=True)
    if "password" in updates:
        user.hashed_password = get_password_hash(updates.pop("password"))
    for field, value in updates.items():
        setattr(user, field, value)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), _=Depends(get_current_platform_admin_user)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return None
