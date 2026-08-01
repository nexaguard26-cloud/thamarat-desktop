"""
Financial Reports Routes
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from typing import Optional

from models.database import get_db
from models.journal import JournalEntry, JournalEntryLine
from models.account import Account, AccountType
from models.fund import Fund
from routes.auth import get_current_user, User

router = APIRouter()

@router.get("/balance-sheet")
async def get_balance_sheet(
    as_of_date: date,
    fund_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate Balance Sheet (الميزانية العمومية)
    Compatible with IPSAS 1
    """
    # Get account types
    asset_type = db.query(AccountType).filter(AccountType.name == 'asset').first()
    liability_type = db.query(AccountType).filter(AccountType.name == 'liability').first()
    equity_type = db.query(AccountType).filter(AccountType.name == 'equity').first()
    
    def get_accounts_by_type(acc_type):
        if not acc_type:
            return []
        
        accounts = db.query(Account).filter(
            Account.account_type_id == acc_type.id,
            Account.is_active == True,
            Account.allows_transactions == True
        ).order_by(Account.code).all()
        
        result = []
        total = 0
        for acc in accounts:
            balance_query = db.query(
                func.coalesce(func.sum(JournalEntryLine.debit_amount), 0),
                func.coalesce(func.sum(JournalEntryLine.credit_amount), 0)
            ).join(JournalEntry).filter(
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
                acc_balance = debit - credit
            else:
                acc_balance = credit - debit
            
            if acc_balance != 0:
                result.append({
                    'code': acc.code,
                    'name': acc.name_ar,
                    'balance': round(acc_balance, 2)
                })
                total += acc_balance
        
        return {'items': result, 'total': round(total, 2)}
    
    assets = get_accounts_by_type(asset_type)
    liabilities = get_accounts_by_type(liability_type)
    equity = get_accounts_by_type(equity_type)
    
    return {
        'report_date': as_of_date,
        'fund_id': fund_id,
        'assets': assets,
        'liabilities': liabilities,
        'equity': equity,
        'totals': {
            'total_assets': assets['total'],
            'total_liabilities': liabilities['total'],
            'total_equity': equity['total'],
            'liabilities_and_equity': liabilities['total'] + equity['total'],
            'is_balanced': abs(assets['total'] - (liabilities['total'] + equity['total'])) < 0.01
        }
    }

@router.get("/income-statement")
async def get_income_statement(
    start_date: date,
    end_date: date,
    fund_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate Income Statement (قائمة الدخل)
    Compatible with IPSAS 1
    """
    revenue_type = db.query(AccountType).filter(AccountType.name == 'revenue').first()
    expense_type = db.query(AccountType).filter(AccountType.name == 'expense').first()
    
    def get_accounts_by_type(acc_type):
        if not acc_type:
            return []
        
        accounts = db.query(Account).filter(
            Account.account_type_id == acc_type.id,
            Account.is_active == True
        ).order_by(Account.code).all()
        
        result = []
        total = 0
        for acc in accounts:
            balance_query = db.query(
                func.coalesce(func.sum(JournalEntryLine.debit_amount), 0),
                func.coalesce(func.sum(JournalEntryLine.credit_amount), 0)
            ).join(JournalEntry).filter(
                JournalEntryLine.account_id == acc.id,
                JournalEntry.status == 'posted',
                JournalEntry.entry_date >= start_date,
                JournalEntry.entry_date <= end_date
            )
            
            if fund_id:
                balance_query = balance_query.filter(JournalEntryLine.fund_id == fund_id)
            
            balance = balance_query.first()
            
            debit = float(balance[0] or 0)
            credit = float(balance[1] or 0)
            
            # For revenue, credit increases; for expense, debit increases
            if acc_type.normal_balance == 'credit':
                acc_balance = credit - debit
            else:
                acc_balance = debit - credit
            
            if acc_balance != 0:
                result.append({
                    'code': acc.code,
                    'name': acc.name_ar,
                    'amount': round(acc_balance, 2)
                })
                total += acc_balance
        
        return {'items': result, 'total': round(total, 2)}
    
    revenues = get_accounts_by_type(revenue_type)
    expenses = get_accounts_by_type(expense_type)
    
    net_surplus = revenues['total'] - expenses['total']
    
    return {
        'period_start': start_date,
        'period_end': end_date,
        'fund_id': fund_id,
        'revenues': revenues,
        'expenses': expenses,
        'result': {
            'net_surplus': round(net_surplus, 2),
            'is_deficit': net_surplus < 0
        }
    }

@router.get("/fund-utilization")
async def get_fund_utilization(
    fund_id: str,
    as_of_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get fund utilization report"""
    fund = db.query(Fund).filter(Fund.id == fund_id).first()
    if not fund:
        return {"error": "الصندوق غير موجود"}
    
    return {
        'fund_id': fund.id,
        'fund_number': fund.fund_number,
        'fund_name': fund.name_ar,
        'fund_type': fund.fund_type,
        'total_allocated': float(fund.total_amount),
        'committed': float(fund.committed_amount or 0),
        'spent': float(fund.spent_amount or 0),
        'available': float(fund.available_amount or fund.total_amount),
        'utilization_percentage': round(fund.utilization_rate, 2),
        'commitment_percentage': round(fund.commitment_rate, 2),
        'currency': fund.currency,
        'end_date': fund.end_date
    }

@router.get("/donor-summary")
async def get_donor_summary(
    donor_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get donor funding summary"""
    from models.fund import Donor
    
    donor = db.query(Donor).filter(Donor.id == donor_id).first()
    if not donor:
        return {"error": "المانح غير موجود"}
    
    funds = db.query(Fund).filter(Fund.donor_id == donor_id).all()
    
    total_allocated = sum(float(f.total_amount) for f in funds)
    total_spent = sum(float(f.spent_amount or 0) for f in funds)
    total_committed = sum(float(f.committed_amount or 0) for f in funds)
    
    return {
        'donor_id': donor.id,
        'donor_name': donor.name_ar,
        'donor_code': donor.code,
        'total_funds': len(funds),
        'total_allocated': total_allocated,
        'total_committed': total_committed,
        'total_spent': total_spent,
        'total_available': total_allocated - total_committed - total_spent,
        'overall_utilization': round((total_spent / total_allocated * 100) if total_allocated > 0 else 0, 2)
    }
