from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.v1.deps import get_db, get_current_platform_admin_user
from schemas.company import CompanyCreate, CompanyRead, CompanyUpdate
from db.models.company import Company

router = APIRouter(prefix="/companies", tags=["companies"])

@router.get("/", response_model=List[CompanyRead])
def list_companies(db: Session = Depends(get_db), _=Depends(get_current_platform_admin_user)):
    return db.query(Company).all()

@router.post("/", response_model=CompanyRead, status_code=201)
def create_company(data: CompanyCreate, db: Session = Depends(get_db), _=Depends(get_current_platform_admin_user)):
    if db.query(Company).filter(Company.domain == data.domain).first():
        raise HTTPException(status_code=400, detail="Domain already exists")
    company = Company(**data.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

@router.get("/{company_id}", response_model=CompanyRead)
def get_company(company_id: int, db: Session = Depends(get_db), _=Depends(get_current_platform_admin_user)):
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.put("/{company_id}", response_model=CompanyRead)
def update_company(company_id: int, data: CompanyUpdate, db: Session = Depends(get_db), _=Depends(get_current_platform_admin_user)):
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(company, field, value)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(company_id: int, db: Session = Depends(get_db), _=Depends(get_current_platform_admin_user)):
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    db.delete(company)
    db.commit()
    return None
