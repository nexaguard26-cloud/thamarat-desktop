"""
Journal Entry Routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal
import uuid
import json

from models.database import get_db
from models.journal import JournalEntry, JournalEntryLine, JournalBatch
from models.fund import Fund
from routes.auth import get_current_user, User
from utils.audit import log_audit

router = APIRouter()

# Pydantic schemas
class JournalLineCreate(BaseModel):
    account_id: str
    description: Optional[str] = None
    debit_amount: float = 0
    credit_amount: float = 0
    fund_id: Optional[str] = None

class JournalEntryCreate(BaseModel):
    entry_date: date
    description: str
    reference: Optional[str] = None
    fund_id: Optional[str] = None
    lines: List[JournalLineCreate]

class JournalEntryResponse(BaseModel):
    id: str
    entry_number: str
    entry_date: date
    description: str
    reference: Optional[str]
    status: str
    fund_id: Optional[str]
    fund_name: Optional[str] = None
    total_debit: float
    total_credit: float
    created_by: Optional[str]
    created_at: datetime
    lines: List[JournalLineCreate]

class TrialBalanceResponse(BaseModel):
    account_code: str
    account_name: str
    account_type: str
    debit_balance: float
    credit_balance: float

@router.get("/", response_model=List[JournalEntryResponse])
async def get_journal_entries(
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    fund_id: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get journal entries with filters"""
    query = db.query(JournalEntry)
    
    if status:
        query = query.filter(JournalEntry.status == status)
    if start_date:
        query = query.filter(JournalEntry.entry_date >= start_date)
    if end_date:
        query = query.filter(JournalEntry.entry_date <= end_date)
    if fund_id:
        query = query.filter(JournalEntry.fund_id == fund_id)
    
    entries = query.order_by(JournalEntry.entry_date.desc(), JournalEntry.entry_number.desc())\
        .offset((page - 1) * limit).limit(limit).all()
    
    result = []
    for entry in entries:
        lines = db.query(JournalEntryLine).filter(JournalEntryLine.entry_id == entry.id).all()
        
        total_debit = sum(float(l.debit_amount or 0) for l in lines)
        total_credit = sum(float(l.credit_amount or 0) for l in lines)
        
        fund_name = None
        if entry.fund_id:
            fund = db.query(Fund).filter(Fund.id == entry.fund_id).first()
            if fund:
                fund_name = fund.name_ar
        
        entry_dict = JournalEntryResponse(
            id=entry.id,
            entry_number=entry.entry_number,
            entry_date=entry.entry_date,
            description=entry.description,
            reference=entry.reference,
            status=entry.status,
            fund_id=entry.fund_id,
            fund_name=fund_name,
            total_debit=total_debit,
            total_credit=total_credit,
            created_by=entry.created_by,
            created_at=entry.created_at,
            lines=[JournalLineCreate(
                account_id=l.account_id,
                description=l.description,
                debit_amount=float(l.debit_amount or 0),
                credit_amount=float(l.credit_amount or 0),
                fund_id=l.fund_id
            ) for l in lines]
        )
        result.append(entry_dict)
    
    return result

@router.get("/{entry_id}", response_model=JournalEntryResponse)
async def get_journal_entry(entry_id: str, db: Session = Depends(get_db)):
    """Get single journal entry"""
    entry = db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="القيد غير موجود")
    
    lines = db.query(JournalEntryLine).filter(JournalEntryLine.entry_id == entry.id).all()
    total_debit = sum(float(l.debit_amount or 0) for l in lines)
    total_credit = sum(float(l.credit_amount or 0) for l in lines)
    
    fund_name = None
    if entry.fund_id:
        fund = db.query(Fund).filter(Fund.id == entry.fund_id).first()
        if fund:
            fund_name = fund.name_ar
    
    return JournalEntryResponse(
        id=entry.id,
        entry_number=entry.entry_number,
        entry_date=entry.entry_date,
        description=entry.description,
        reference=entry.reference,
        status=entry.status,
        fund_id=entry.fund_id,
        fund_name=fund_name,
        total_debit=total_debit,
        total_credit=total_credit,
        created_by=entry.created_by,
        created_at=entry.created_at,
        lines=[JournalLineCreate(
            account_id=l.account_id,
            description=l.description,
            debit_amount=float(l.debit_amount or 0),
            credit_amount=float(l.credit_amount or 0),
            fund_id=l.fund_id
        ) for l in lines]
    )

@router.post("/", response_model=JournalEntryResponse)
async def create_journal_entry(
    data: JournalEntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new journal entry (double-entry validation required)"""
    # Validate double-entry: total debits must equal total credits
    total_debit = sum(l.debit_amount for l in data.lines)
    total_credit = sum(l.credit_amount for l in data.lines)
    
    if abs(total_debit - total_credit) > 0.01:
        raise HTTPException(
            status_code=400,
            detail=f"خطأ في القيد المزدوج: المدين ({total_debit}) لا يساوي الدائن ({total_credit})"
        )
    
    # Generate entry number
    last_entry = db.query(JournalEntry).order_by(JournalEntry.created_at.desc()).first()
    last_num = int(last_entry.entry_number.split('-')[-1]) if last_entry else 0
    entry_number = f"JE-{datetime.now().year}-{str(last_num + 1).zfill(6)}"
    
    # Create entry
    entry = JournalEntry(
        id=str(uuid.uuid4()),
        entry_number=entry_number,
        entry_date=data.entry_date,
        description=data.description,
        reference=data.reference,
        fund_id=data.fund_id,
        status='draft',
        created_by=current_user.id
    )
    
    db.add(entry)
    db.flush()
    
    # Create lines
    lines_data = []
    for line in data.lines:
        journal_line = JournalEntryLine(
            id=str(uuid.uuid4()),
            entry_id=entry.id,
            account_id=line.account_id,
            description=line.description,
            debit_amount=Decimal(str(line.debit_amount)),
            credit_amount=Decimal(str(line.credit_amount)),
            fund_id=line.fund_id or data.fund_id
        )
        db.add(journal_line)
        lines_data.append(line)
    
    db.commit()
    db.refresh(entry)
    
    log_audit(db, current_user.id, "create", "journal_entry", entry.id, None, data.model_dump())
    
    return JournalEntryResponse(
        id=entry.id,
        entry_number=entry.entry_number,
        entry_date=entry.entry_date,
        description=entry.description,
        reference=entry.reference,
        status=entry.status,
        fund_id=entry.fund_id,
        total_debit=total_debit,
        total_credit=total_credit,
        created_by=entry.created_by,
        created_at=entry.created_at,
        lines=data.lines
    )

@router.post("/{entry_id}/post")
async def post_journal_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Post (approve) journal entry"""
    entry = db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="القيد غير موجود")
    
    if entry.status != 'draft':
        raise HTTPException(status_code=400, detail="لا يمكن ترحيل القيد")
    
    entry.status = 'posted'
    entry.posted_at = datetime.utcnow()
    entry.posted_by = current_user.id
    
    db.commit()
    
    log_audit(db, current_user.id, "post", "journal_entry", entry.id)
    
    return {"message": "تم ترحيل القيد بنجاح", "entry_number": entry.entry_number}

@router.post("/{entry_id}/reverse")
async def reverse_journal_entry(
    entry_id: str,
    reason: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reverse journal entry"""
    entry = db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="القيد غير موجود")
    
    if entry.status != 'posted':
        raise HTTPException(status_code=400, detail="لا يمكن إلغاء القيد")
    
    # Create reversal entry
    lines = db.query(JournalEntryLine).filter(JournalEntryLine.entry_id == entry.id).all()
    
    last_entry = db.query(JournalEntry).order_by(JournalEntry.created_at.desc()).first()
    last_num = int(last_entry.entry_number.split('-')[-1]) if last_entry else 0
    reversal_number = f"JE-{datetime.now().year}-{str(last_num + 1).zfill(6)}"
    
    reversal = JournalEntry(
        id=str(uuid.uuid4()),
        entry_number=reversal_number,
        entry_date=date.today(),
        description=f"إلغاء: {entry.description} - {reason}",
        reference=f"REV:{entry.entry_number}",
        fund_id=entry.fund_id,
        status='posted',
        created_by=current_user.id,
        posted_at=datetime.utcnow(),
        posted_by=current_user.id
    )
    db.add(reversal)
    db.flush()
    
    # Create reversed lines (swap debit/credit)
    for line in lines:
        reversal_line = JournalEntryLine(
            id=str(uuid.uuid4()),
            entry_id=reversal.id,
            account_id=line.account_id,
            description=f"إلغاء: {line.description or ''}",
            debit_amount=line.credit_amount,
            credit_amount=line.debit_amount,
            fund_id=line.fund_id
        )
        db.add(reversal_line)
    
    # Mark original as reversed
    entry.status = 'reversed'
    entry.reversed_at = datetime.utcnow()
    entry.reversed_by = current_user.id
    entry.reversal_reason = reason
    
    db.commit()
    
    log_audit(db, current_user.id, "reverse", "journal_entry", entry.id, None, {"reason": reason})
    
    return {"message": "تم إلغاء القيد بنجاح", "reversal_number": reversal_number}

@router.get("/reports/trial-balance")
async def get_trial_balance(
    as_of_date: date,
    fund_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Generate trial balance report"""
    from models.account import Account, AccountType
    
    # Get all accounts
    query = db.query(Account, AccountType).join(
        AccountType, Account.account_type_id == AccountType.id
    ).filter(Account.is_active == True, Account.allows_transactions == True)
    
    if fund_id:
        query = query.filter(Account.is_control_account == False)
    
    accounts = query.order_by(Account.code).all()
    
    result = []
    total_debit = 0
    total_credit = 0
    
    for acc, acc_type in accounts:
        # Get account balance
        balance_query = db.query(
            func.coalesce(func.sum(JournalEntryLine.debit_amount), 0),
            func.coalesce(func.sum(JournalEntryLine.credit_amount), 0)
        ).filter(
            JournalEntryLine.account_id == acc.id,
            JournalEntry.status == 'posted',
            JournalEntry.entry_date <= as_of_date
        )
        
        if fund_id:
            balance_query = balance_query.filter(JournalEntryLine.fund_id == fund_id)
        
        balance = balance_query.first()
        
        debit = float(balance[0] or 0)
        credit = float(balance[1] or 0)
        
        if acc_type.normal_balance == 'debit':
            debit_balance = debit - credit
            credit_balance = 0
            if debit_balance < 0:
                credit_balance = abs(debit_balance)
                debit_balance = 0
        else:
            credit_balance = credit - debit
            debit_balance = 0
            if credit_balance < 0:
                debit_balance = abs(credit_balance)
                credit_balance = 0
        
        if debit_balance > 0 or credit_balance > 0:
            result.append({
                'account_code': acc.code,
                'account_name': acc.name_ar,
                'account_type': acc_type.name_ar,
                'debit_balance': round(debit_balance, 2),
                'credit_balance': round(credit_balance, 2)
            })
            total_debit += debit_balance
            total_credit += credit_balance
    
    return {
        'as_of_date': as_of_date,
        'fund_id': fund_id,
        'accounts': result,
        'totals': {
            'total_debit': round(total_debit, 2),
            'total_credit': round(total_credit, 2),
            'is_balanced': abs(total_debit - total_credit) < 0.01
        }
    }
