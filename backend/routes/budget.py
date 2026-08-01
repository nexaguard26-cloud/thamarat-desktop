"""
Budget Management Routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal
import uuid

from models.database import get_db
from models.budget import Budget, BudgetLine
from routes.auth import get_current_user, User
from utils.audit import log_audit

router = APIRouter()

# Pydantic schemas
class BudgetLineCreate(BaseModel):
    account_id: str
    account_code: str
    account_name: str
    original_amount: float
    period_start: Optional[date] = None
    period_end: Optional[date] = None

class BudgetCreate(BaseModel):
    fiscal_year: int
    description: Optional[str] = None
    fund_id: Optional[str] = None
    lines: List[BudgetLineCreate]

class BudgetLineResponse(BaseModel):
    id: str
    account_id: str
    account_code: str
    account_name: str
    original_amount: float
    revised_amount: Optional[float]
    committed_amount: float
    actual_amount: float
    available_amount: float
    utilization_rate: float

class BudgetResponse(BaseModel):
    id: str
    budget_number: str
    fiscal_year: int
    version: int
    description: Optional[str]
    total_amount: float
    total_committed: float
    total_actual: float
    status: str
    is_current: bool
    created_at: datetime

@router.get("/", response_model=List[BudgetResponse])
async def get_budgets(
    fiscal_year: Optional[int] = None,
    status: Optional[str] = None,
    fund_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all budgets"""
    query = db.query(Budget)
    
    if fiscal_year:
        query = query.filter(Budget.fiscal_year == fiscal_year)
    if status:
        query = query.filter(Budget.status == status)
    if fund_id:
        query = query.filter(Budget.fund_id == fund_id)
    
    budgets = query.order_by(Budget.fiscal_year.desc(), Budget.version.desc()).all()
    
    result = []
    for budget in budgets:
        lines = db.query(BudgetLine).filter(BudgetLine.budget_id == budget.id).all()
        
        total = sum(float(l.original_amount) for l in lines)
        total_committed = sum(float(l.committed_amount or 0) for l in lines)
        total_actual = sum(float(l.actual_amount or 0) for l in lines)
        
        result.append(BudgetResponse(
            id=budget.id,
            budget_number=budget.budget_number,
            fiscal_year=budget.fiscal_year,
            version=budget.version,
            description=budget.description,
            total_amount=total,
            total_committed=total_committed,
            total_actual=total_actual,
            status=budget.status,
            is_current=budget.is_current == 'true',
            created_at=budget.created_at
        ))
    
    return result

@router.get("/{budget_id}")
async def get_budget(budget_id: str, db: Session = Depends(get_db)):
    """Get single budget with lines"""
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="الميزانية غير موجودة")
    
    lines = db.query(BudgetLine).filter(BudgetLine.budget_id == budget.id).all()
    
    budget_response = BudgetResponse(
        id=budget.id,
        budget_number=budget.budget_number,
        fiscal_year=budget.fiscal_year,
        version=budget.version,
        description=budget.description,
        total_amount=sum(float(l.original_amount) for l in lines),
        total_committed=sum(float(l.committed_amount or 0) for l in lines),
        total_actual=sum(float(l.actual_amount or 0) for l in lines),
        status=budget.status,
        is_current=budget.is_current == 'true',
        created_at=budget.created_at
    )
    
    lines_response = []
    for line in lines:
        lines_response.append(BudgetLineResponse(
            id=line.id,
            account_id=line.account_id,
            account_code=line.account_code,
            account_name=line.account_name,
            original_amount=float(line.original_amount),
            revised_amount=float(line.revised_amount) if line.revised_amount else None,
            committed_amount=float(line.committed_amount or 0),
            actual_amount=float(line.actual_amount or 0),
            available_amount=line.available_amount,
            utilization_rate=line.utilization_rate
        ))
    
    return {
        "budget": budget_response,
        "lines": lines_response
    }

@router.post("/", response_model=BudgetResponse)
async def create_budget(
    data: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new budget"""
    # Generate budget number
    last_budget = db.query(Budget).filter(
        Budget.fiscal_year == data.fiscal_year
    ).order_by(Budget.version.desc()).first()
    
    version = (last_budget.version + 1) if last_budget else 1
    budget_number = f"BUD-{data.fiscal_year}-{str(version).zfill(3)}"
    
    # Create budget
    budget = Budget(
        id=str(uuid.uuid4()),
        budget_number=budget_number,
        fiscal_year=data.fiscal_year,
        version=version,
        description=data.description,
        fund_id=data.fund_id,
        status='draft',
        is_current='true',
        created_by=current_user.id
    )
    db.add(budget)
    db.flush()
    
    # Create budget lines
    for line_data in data.lines:
        line = BudgetLine(
            id=str(uuid.uuid4()),
            budget_id=budget.id,
            account_id=line_data.account_id,
            account_code=line_data.account_code,
            account_name=line_data.account_name,
            original_amount=Decimal(str(line_data.original_amount)),
            committed_amount=Decimal('0'),
            actual_amount=Decimal('0'),
            period_start=line_data.period_start,
            period_end=line_data.period_end
        )
        db.add(line)
    
    db.commit()
    db.refresh(budget)
    
    log_audit(db, current_user.id, "create", "budget", budget.id, None, data.model_dump())
    
    return BudgetResponse(
        id=budget.id,
        budget_number=budget.budget_number,
        fiscal_year=budget.fiscal_year,
        version=budget.version,
        description=budget.description,
        total_amount=sum(l.original_amount for l in data.lines),
        total_committed=0,
        total_actual=0,
        status=budget.status,
        is_current=True,
        created_at=budget.created_at
    )

@router.post("/{budget_id}/approve")
async def approve_budget(
    budget_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve budget"""
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="الميزانية غير موجودة")
    
    if budget.status != 'draft':
        raise HTTPException(status_code=400, detail="لا يمكن اعتماد الميزانية")
    
    budget.status = 'approved'
    budget.approved_by = current_user.id
    budget.approved_at = datetime.utcnow()
    
    db.commit()
    
    log_audit(db, current_user.id, "approve", "budget", budget.id)
    
    return {"message": "تم اعتماد الميزانية بنجاح"}
