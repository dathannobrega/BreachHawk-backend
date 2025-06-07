from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.v1.deps import get_db, get_current_platform_admin_user
from schemas.plan import PlanCreate, PlanRead, PlanUpdate
from db.models.plan import Plan

router = APIRouter(prefix="/plans", tags=["plans"])

@router.get("/", response_model=List[PlanRead])
def list_plans(db: Session = Depends(get_db), _=Depends(get_current_platform_admin_user)):
    return db.query(Plan).all()

@router.post("/", response_model=PlanRead, status_code=201)
def create_plan(data: PlanCreate, db: Session = Depends(get_db), _=Depends(get_current_platform_admin_user)):
    if db.query(Plan).filter(Plan.name == data.name).first():
        raise HTTPException(status_code=400, detail="Plan already exists")
    plan = Plan(**data.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan

@router.get("/{plan_id}", response_model=PlanRead)
def get_plan(plan_id: int, db: Session = Depends(get_db), _=Depends(get_current_platform_admin_user)):
    plan = db.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

@router.put("/{plan_id}", response_model=PlanRead)
def update_plan(plan_id: int, data: PlanUpdate, db: Session = Depends(get_db), _=Depends(get_current_platform_admin_user)):
    plan = db.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(plan, field, value)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan

@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(plan_id: int, db: Session = Depends(get_db), _=Depends(get_current_platform_admin_user)):
    plan = db.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    db.delete(plan)
    db.commit()
    return None
