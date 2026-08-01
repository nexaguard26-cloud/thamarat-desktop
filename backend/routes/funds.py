"""
Fund Accounting Routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal
import uuid

from models.database import get_db
from models.fund import Fund, Donor, FundingAgreement
from routes.auth import get_current_user, User
from utils.audit import log_audit

router = APIRouter()

# Pydantic schemas
class DonorCreate(BaseModel):
    code: str
    name_ar: str
    name_en: Optional[str] = None
    donor_type: Optional[str] = None
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None

class FundCreate(BaseModel):
    fund_number: str
    name_ar: str
    name_en: Optional[str] = None
    fund_type: str  # unrestricted, restricted, temporarily_restricted
    restriction_type: Optional[str] = None
    total_amount: float
    currency: str = "USD"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    donor_id: Optional[str] = None
    funding_agreement_id: Optional[str] = None
    notes: Optional[str] = None

class FundResponse(BaseModel):
    id: str
    fund_number: str
    name_ar: str
    name_en: Optional[str]
    fund_type: str
    restriction_type: Optional[str]
    total_amount: float
    available_amount: float
    committed_amount: float
    spent_amount: float
    currency: str
    utilization_rate: float
    commitment_rate: float
    status: str
    donor_name: Optional[str] = None

# Donors
@router.get("/donors", response_model=List[dict])
async def get_donors(
    donor_type: Optional[str] = None,
    is_active: Optional[bool] = True,
    db: Session = Depends(get_db)
):
    """Get all donors"""
    query = db.query(Donor)
    if is_active is not None:
        query = query.filter(Donor.is_active == str(is_active).lower())
    if donor_type:
        query = query.filter(Donor.donor_type == donor_type)
    return query.order_by(Donor.name_ar).all()

@router.post("/donors")
async def create_donor(
    data: DonorCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new donor"""
    existing = db.query(Donor).filter(Donor.code == data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="رمز المانح موجود مسبقاً")
    
    donor = Donor(
        id=str(uuid.uuid4()),
        **data.model_dump(),
        is_active='true'
    )
    db.add(donor)
    db.commit()
    db.refresh(donor)
    
    log_audit(db, current_user.id, "create", "donor", donor.id, None, data.model_dump())
    return donor

# Funds
@router.get("/", response_model=List[FundResponse])
async def get_funds(
    status: Optional[str] = None,
    fund_type: Optional[str] = None,
    donor_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all funds"""
    query = db.query(Fund)
    
    if status:
        query = query.filter(Fund.status == status)
    if fund_type:
        query = query.filter(Fund.fund_type == fund_type)
    if donor_id:
        query = query.filter(Fund.donor_id == donor_id)
    
    funds = query.order_by(Fund.fund_number.desc()).all()
    
    result = []
    for fund in funds:
        donor_name = None
        if fund.donor_id:
            donor = db.query(Donor).filter(Donor.id == fund.donor_id).first()
            if donor:
                donor_name = donor.name_ar
        
        result.append(FundResponse(
            id=fund.id,
            fund_number=fund.fund_number,
            name_ar=fund.name_ar,
            name_en=fund.name_en,
            fund_type=fund.fund_type,
            restriction_type=fund.restriction_type,
            total_amount=float(fund.total_amount),
            available_amount=float(fund.available_amount or fund.total_amount),
            committed_amount=float(fund.committed_amount or 0),
            spent_amount=float(fund.spent_amount or 0),
            currency=fund.currency,
            utilization_rate=fund.utilization_rate,
            commitment_rate=fund.commitment_rate,
            status=fund.status,
            donor_name=donor_name
        ))
    
    return result

@router.get("/{fund_id}")
async def get_fund(fund_id: str, db: Session = Depends(get_db)):
    """Get single fund with details"""
    fund = db.query(Fund).filter(Fund.id == fund_id).first()
    if not fund:
        raise HTTPException(status_code=404, detail="الصندوق غير موجود")
    
    donor = None
    if fund.donor_id:
        donor = db.query(Donor).filter(Donor.id == fund.donor_id).first()
    
    agreement = None
    if fund.funding_agreement_id:
        agreement = db.query(FundingAgreement).filter(
            FundingAgreement.id == fund.funding_agreement_id
        ).first()
    
    return {
        **FundResponse.model_validate(fund).model_dump(),
        "donor": donor,
        "agreement": agreement
    }

@router.post("/", response_model=FundResponse)
async def create_fund(
    data: FundCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new fund"""
    existing = db.query(Fund).filter(Fund.fund_number == data.fund_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="رقم الصندوق موجود مسبقاً")
    
    fund = Fund(
        id=str(uuid.uuid4()),
        fund_number=data.fund_number,
        name_ar=data.name_ar,
        name_en=data.name_en,
        fund_type=data.fund_type,
        restriction_type=data.restriction_type,
        total_amount=Decimal(str(data.total_amount)),
        available_amount=Decimal(str(data.total_amount)),
        committed_amount=Decimal('0'),
        spent_amount=Decimal('0'),
        currency=data.currency,
        start_date=data.start_date,
        end_date=data.end_date,
        donor_id=data.donor_id,
        funding_agreement_id=data.funding_agreement_id,
        notes=data.notes,
        status='active'
    )
    
    db.add(fund)
    db.commit()
    db.refresh(fund)
    
    log_audit(db, current_user.id, "create", "fund", fund.id, None, data.model_dump())
    
    return FundResponse.model_validate(fund)

@router.put("/{fund_id}/close")
async def close_fund(
    fund_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Close a fund"""
    fund = db.query(Fund).filter(Fund.id == fund_id).first()
    if not fund:
        raise HTTPException(status_code=404, detail="الصندوق غير موجود")
    
    fund.status = 'closed'
    db.commit()
    
    log_audit(db, current_user.id, "close", "fund", fund.id)
    
    return {"message": "تم إغلاق الصندوق بنجاح"}
