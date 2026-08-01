"""
Journal Entry Models
"""

from sqlalchemy import Column, String, Date, DateTime, Numeric, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class JournalBatch(Base):
    __tablename__ = "journal_batches"
    
    id = Column(String, primary_key=True)
    batch_number = Column(String, unique=True, nullable=False, index=True)
    description = Column(String)
    status = Column(String, default='open')  # open, closed
    entry_count = Column(Integer, default=0)
    total_debit = Column(Numeric(15, 2), default=0)
    total_credit = Column(Numeric(15, 2), default=0)
    created_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime)

class JournalEntry(Base):
    __tablename__ = "journal_entries"
    
    id = Column(String, primary_key=True)
    entry_number = Column(String, unique=True, nullable=False, index=True)
    entry_date = Column(Date, nullable=False, index=True)
    batch_id = Column(String, ForeignKey("journal_batches.id"))
    description = Column(Text)
    reference = Column(String)
    status = Column(String, default='draft')  # draft, posted, reversed
    fund_id = Column(String, ForeignKey("funds.id"))
    project_id = Column(String)
    created_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    posted_at = Column(DateTime)
    posted_by = Column(String, ForeignKey("users.id"))
    reversed_at = Column(DateTime)
    reversed_by = Column(String, ForeignKey("users.id"))
    reversal_reason = Column(Text)
    
    # Relationships
    batch = relationship("JournalBatch", backref="entries")
    fund = relationship("Fund")
    lines = relationship("JournalEntryLine", back_populates="entry", cascade="all, delete-orphan")

class JournalEntryLine(Base):
    __tablename__ = "journal_entry_lines"
    
    id = Column(String, primary_key=True)
    entry_id = Column(String, ForeignKey("journal_entries.id"), nullable=False)
    account_id = Column(String, ForeignKey("accounts.id"), nullable=False)
    description = Column(String)
    debit_amount = Column(Numeric(15, 2), default=0)
    credit_amount = Column(Numeric(15, 2), default=0)
    fund_id = Column(String, ForeignKey("funds.id"))
    project_id = Column(String)
    cost_center_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    entry = relationship("JournalEntry", back_populates="lines")
    account = relationship("Account", back_populates="journal_lines")
    fund = relationship("Fund")
    
    @property
    def is_debit(self):
        return self.debit_amount and self.debit_amount > 0
    
    @property
    def is_credit(self):
        return self.credit_amount and self.credit_amount > 0
