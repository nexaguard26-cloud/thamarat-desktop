"""
Fund Accounting Models
"""

from sqlalchemy import Column, String, Date, DateTime, Numeric, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Donor(Base):
    __tablename__ = "donors"
    
    id = Column(String, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    name_ar = Column(String, nullable=False)
    name_en = Column(String)
    donor_type = Column(String)  # un, usaid, echo, fcdo, giz, custom
    contact_person = Column(String)
    contact_email = Column(String)
    contact_phone = Column(String)
    address = Column(Text)
    is_active = Column(Boolean, default=True) if hasattr(Boolean, '__class__') else Column(String, default='true')
    is_active = Column(String, default='true')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    agreements = relationship("FundingAgreement", back_populates="donor")
    funds = relationship("Fund", back_populates="donor")

class FundingAgreement(Base):
    __tablename__ = "funding_agreements"
    
    id = Column(String, primary_key=True)
    donor_id = Column(String, ForeignKey("donors.id"), nullable=False)
    agreement_number = Column(String, unique=True, nullable=False)
    title_ar = Column(String)
    title_en = Column(String)
    description = Column(Text)
    total_amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String, default='USD')
    start_date = Column(Date)
    end_date = Column(Date)
    reporting_frequency = Column(String)  # monthly, quarterly, semi_annual, annual
    status = Column(String, default='draft')  # draft, active, completed, terminated
    indirect_cost_rate = Column(Numeric(5, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    donor = relationship("Donor", back_populates="agreements")
    funds = relationship("Fund", back_populates="agreement")

class Fund(Base):
    __tablename__ = "funds"
    
    id = Column(String, primary_key=True)
    funding_agreement_id = Column(String, ForeignKey("funding_agreements.id"))
    donor_id = Column(String, ForeignKey("donors.id"))
    fund_number = Column(String, unique=True, nullable=False, index=True)
    name_ar = Column(String, nullable=False)
    name_en = Column(String)
    fund_type = Column(String)  # unrestricted, restricted, temporarily_restricted
    restriction_type = Column(String)  # purpose, time, donor
    total_amount = Column(Numeric(15, 2), nullable=False)
    available_amount = Column(Numeric(15, 2))
    committed_amount = Column(Numeric(15, 2), default=0)
    spent_amount = Column(Numeric(15, 2), default=0)
    currency = Column(String, default='USD')
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String, default='active')  # active, closed, completed
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    agreement = relationship("FundingAgreement", back_populates="funds")
    donor = relationship("Donor", back_populates="funds")
    journal_entries = relationship("JournalEntry", back_populates="fund")
    
    @property
    def utilization_rate(self):
        if not self.total_amount or self.total_amount == 0:
            return 0
        return float(self.spent_amount or 0) / float(self.total_amount) * 100
    
    @property
    def commitment_rate(self):
        if not self.total_amount or self.total_amount == 0:
            return 0
        committed = float(self.committed_amount or 0) + float(self.spent_amount or 0)
        return committed / float(self.total_amount) * 100
