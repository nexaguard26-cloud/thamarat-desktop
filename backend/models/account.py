"""
Chart of Accounts Models
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class AccountType(Base):
    __tablename__ = "account_types"
    
    id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False)  # asset, liability, equity, revenue, expense
    name_ar = Column(String)
    name_en = Column(String)
    category = Column(String)  # asset, liability, equity, revenue, expense
    normal_balance = Column(String)  # debit, credit
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    accounts = relationship("Account", back_populates="account_type")

class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(String, primary_key=True)
    code = Column(String, unique=True, nullable=False, index=True)
    name_ar = Column(String, nullable=False)
    name_en = Column(String)
    description = Column(String)
    account_type_id = Column(String, ForeignKey("account_types.id"))
    parent_id = Column(String, ForeignKey("accounts.id"))
    level = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_control_account = Column(Boolean, default=False)
    allows_transactions = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    account_type = relationship("AccountType", back_populates="accounts")
    parent = relationship("Account", remote_side=[id], backref="children")
    journal_lines = relationship("JournalEntryLine", back_populates="account")
    
    @property
    def balance(self):
        """Calculate account balance from journal entries"""
        from sqlalchemy import func
        from models.journal import JournalEntryLine
        
        db = next(Base.metadata.bind.connect().__class__())
        try:
            result = db.query(
                func.coalesce(func.sum(JournalEntryLine.debit_amount), 0),
                func.coalesce(func.sum(JournalEntryLine.credit_amount), 0)
            ).filter(
                JournalEntryLine.account_id == self.id
            ).first()
            
            if self.account_type and self.account_type.normal_balance == 'debit':
                return float(result[0] or 0) - float(result[1] or 0)
            else:
                return float(result[1] or 0) - float(result[0] or 0)
        finally:
            db.close()
