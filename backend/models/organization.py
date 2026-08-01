"""
Organization Settings Model
"""

from sqlalchemy import Column, String, Date, DateTime, Text
from datetime import datetime
from .database import Base

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(String, primary_key=True)
    name_ar = Column(String, nullable=False)
    name_en = Column(String)
    registration_number = Column(String)
    tax_id = Column(String)
    address = Column(Text)
    phone = Column(String)
    email = Column(String)
    website = Column(String)
    logo_path = Column(String)
    fiscal_year_start = Column(Date)
    base_currency = Column(String, default='YER')
    secondary_currency = Column(String, default='USD')
    date_format = Column(String, default='DD/MM/YYYY')
    is_active = Column(String, default='true')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
