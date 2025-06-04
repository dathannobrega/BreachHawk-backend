from fastapi import APIRouter, Depends
from api.v1.deps import get_current_platform_admin_user
from services import stripe_service
from typing import List
from schemas.billing import Invoice, Payment, Subscription

router = APIRouter(prefix="/billing", tags=["billing"])

@router.get("/invoices", response_model=List[Invoice])
def get_invoices(_=Depends(get_current_platform_admin_user)):
    return stripe_service.list_invoices()

@router.get("/payments", response_model=List[Payment])
def get_payments(_=Depends(get_current_platform_admin_user)):
    return stripe_service.list_payments()

@router.get("/subscriptions", response_model=List[Subscription])
def get_subscriptions(_=Depends(get_current_platform_admin_user)):
    return stripe_service.list_subscriptions()
