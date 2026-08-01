"""
Chart of Accounts Routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from pydantic import BaseModel
import uuid

from models.database import get_db
from models.account import Account, AccountType
from models.journal import JournalEntryLine
from routes.auth import get_current_user, User
from utils.audit import log_audit

router = APIRouter()

# Pydantic schemas
class AccountTypeResponse(BaseModel):
    id: str
    name: str
    name_ar: Optional[str]
    name_en: Optional[str]
    normal_balance: str

class AccountCreate(BaseModel):
    code: str
    name_ar: str
    name_en: Optional[str] = None
    description: Optional[str] = None
    account_type_id: str
    parent_id: Optional[str] = None
    is_control_account: bool = False
    allows_transactions: bool = True

class AccountResponse(BaseModel):
    id: str
    code: str
    name_ar: str
    name_en: Optional[str]
    description: Optional[str]
    account_type_id: str
    account_type_name: Optional[str] = None
    parent_id: Optional[str]
    level: int
    is_active: bool
    is_control_account: bool
    balance: float = 0

@router.get("/types", response_model=List[AccountTypeResponse])
async def get_account_types(db: Session = Depends(get_db)):
    """Get all account types"""
    types = db.query(AccountType).order_by(AccountType.display_order).all()
    return types

@router.get("/", response_model=List[AccountResponse])
async def get_accounts(
    account_type_id: Optional[str] = None,
    is_active: Optional[bool] = True,
    parent_id: Optional[str] = None,
    level: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all accounts with optional filters"""
    query = db.query(Account)
    
    if account_type_id:
        query = query.filter(Account.account_type_id == account_type_id)
    if is_active is not None:
        query = query.filter(Account.is_active == is_active)
    if parent_id is not None:
        query = query.filter(Account.parent_id == parent_id)
    if level is not None:
        query = query.filter(Account.level == level)
    
    accounts = query.order_by(Account.code).all()
    
    # Calculate balances
    result = []
    for acc in accounts:
        balance = db.query(
            func.coalesce(func.sum(JournalEntryLine.debit_amount), 0),
            func.coalesce(func.sum(JournalEntryLine.credit_amount), 0)
        ).filter(JournalEntryLine.account_id == acc.id).first()
        
        debit = float(balance[0] or 0)
        credit = float(balance[1] or 0)
        
        if acc.account_type and acc.account_type.normal_balance == 'debit':
            acc_balance = debit - credit
        else:
            acc_balance = credit - debit
        
        acc_dict = AccountResponse.model_validate(acc)
        acc_dict.balance = acc_balance
        if acc.account_type:
            acc_dict.account_type_name = acc.account_type.name_ar
        result.append(acc_dict)
    
    return result

@router.get("/tree")
async def get_account_tree(db: Session = Depends(get_db)):
    """Get accounts as hierarchical tree"""
    # Get all accounts with their types
    accounts = db.query(Account, AccountType).join(
        AccountType, Account.account_type_id == AccountType.id
    ).filter(Account.is_active == True).order_by(Account.code).all()
    
    # Build tree structure
    tree = []
    accounts_dict = {}
    
    for acc, acc_type in accounts:
        balance = db.query(
            func.coalesce(func.sum(JournalEntryLine.debit_amount), 0),
            func.coalesce(func.sum(JournalEntryLine.credit_amount), 0)
        ).filter(JournalEntryLine.account_id == acc.id).first()
        
        debit = float(balance[0] or 0)
        credit = float(balance[1] or 0)
        
        if acc_type.normal_balance == 'debit':
            acc_balance = debit - credit
        else:
            acc_balance = credit - debit
        
        node = {
            'id': acc.id,
            'code': acc.code,
            'name_ar': acc.name_ar,
            'name_en': acc.name_en,
            'type': acc_type.name_ar,
            'balance': acc_balance,
            'level': acc.level,
            'children': []
        }
        accounts_dict[acc.id] = node
    
    # Build hierarchy
    for acc, _ in accounts:
        if acc.parent_id and acc.parent_id in accounts_dict:
            accounts_dict[acc.parent_id]['children'].append(accounts_dict[acc.id])
        elif acc.level == 0 or not acc.parent_id:
            tree.append(accounts_dict[acc.id])
    
    return tree

@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(account_id: str, db: Session = Depends(get_db)):
    """Get single account"""
    acc = db.query(Account).filter(Account.id == account_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="الحساب غير موجود")
    
    balance = db.query(
        func.coalesce(func.sum(JournalEntryLine.debit_amount), 0),
        func.coalesce(func.sum(JournalEntryLine.credit_amount), 0)
    ).filter(JournalEntryLine.account_id == acc.id).first()
    
    debit = float(balance[0] or 0)
    credit = float(balance[1] or 0)
    
    if acc.account_type and acc.account_type.normal_balance == 'debit':
        acc_balance = debit - credit
    else:
        acc_balance = credit - debit
    
    result = AccountResponse.model_validate(acc)
    result.balance = acc_balance
    if acc.account_type:
        result.account_type_name = acc.account_type.name_ar
    
    return result

@router.post("/", response_model=AccountResponse)
async def create_account(
    data: AccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new account"""
    # Check if code exists
    existing = db.query(Account).filter(Account.code == data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="رمز الحساب موجود مسبقاً")
    
    # Get account type
    acc_type = db.query(AccountType).filter(AccountType.id == data.account_type_id).first()
    if not acc_type:
        raise HTTPException(status_code=400, detail="نوع الحساب غير موجود")
    
    # Calculate level
    level = 0
    if data.parent_id:
        parent = db.query(Account).filter(Account.id == data.parent_id).first()
        if parent:
            level = parent.level + 1
    
    account = Account(
        id=str(uuid.uuid4()),
        code=data.code,
        name_ar=data.name_ar,
        name_en=data.name_en,
        description=data.description,
        account_type_id=data.account_type_id,
        parent_id=data.parent_id,
        level=level,
        is_control_account=data.is_control_account,
        allows_transactions=data.allows_transactions,
        is_active=True
    )
    
    db.add(account)
    db.commit()
    db.refresh(account)
    
    log_audit(db, current_user.id, "create", "account", account.id, None, data.model_dump())
    
    return AccountResponse.model_validate(account)

@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: str,
    data: AccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update account"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="الحساب غير موجود")
    
    old_data = AccountCreate.model_validate(account)
    
    for key, value in data.model_dump().items():
        setattr(account, key, value)
    
    db.commit()
    db.refresh(account)
    
    log_audit(db, current_user.id, "update", "account", account.id, old_data, data.model_dump())
    
    return AccountResponse.model_validate(account)

@router.delete("/{account_id}")
async def delete_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deactivate account (soft delete)"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="الحساب غير موجود")
    
    account.is_active = False
    db.commit()
    
    log_audit(db, current_user.id, "delete", "account", account.id)
    
    return {"message": "تم حذف الحساب"}
