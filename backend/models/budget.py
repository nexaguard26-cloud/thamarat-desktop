"""
Budget Models
"""

from sqlalchemy import Column, String, Date, DateTime, Numeric, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Budget(Base):
    __tablename__ = "budgets"
    
    id = Column(String, primary_key=True)
    budget_number = Column(String, unique=True, nullable=False, index=True)
    fiscal_year = Column(Integer, nullable=False)
    version = Column(Integer, default=1)
    description = Column(Text)
    fund_id = Column(String, ForeignKey("funds.id"))
    total_amount = Column(Numeric(15, 2))
    status = Column(String, default='draft')  # draft, approved, closed
    is_current = Column(String, default='true')
    approved_by = Column(String, ForeignKey("users.id"))
    approved_at = Column(DateTime)
    created_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    fund = relationship("Fund")
    lines = relationship("BudgetLine", back_populates="budget", cascade="all, delete-orphan")

class BudgetLine(Base):
    __tablename__ = "budget_lines"
    
    id = Column(String, primary_key=True)
    budget_id = Column(String, ForeignKey("budgets.id"), nullable=False)
    account_id = Column(String, ForeignKey("accounts.id"), nullable=False)
    account_code = Column(String)
    account_name = Column(String)
    original_amount = Column(Numeric(15, 2), nullable=False)
    revised_amount = Column(Numeric(15, 2))
    committed_amount = Column(Numeric(15, 2), default=0)
    actual_amount = Column(Numeric(15, 2), default=0)
    period_start = Column(Date)
    period_end = Column(Date)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    budget = relationship("Budget", back_populates="lines")
    account = relationship("Account")
    
    @property
    def available_amount(self):
        amount = self.revised_amount or self.original_amount
        return float(amount) - float(self.committed_amount or 0) - float(self.actual_amount or 0)
    
    @property
    def utilization_rate(self):
        amount = self.revised_amount or self.original_amount
        if not amount or amount == 0:
            return 0
        return (float(self.actual_amount or 0) / float(amount)) * 100
