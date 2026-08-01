"""
Audit Log Model - Immutable audit trail
"""

from sqlalchemy import Column, String, DateTime, Text, Numeric
from datetime import datetime
from .database import Base
import hashlib
import json

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True)
    user_id = Column(String)
    user_name = Column(String)
    action = Column(String, nullable=False)  # create, update, delete, login, logout, post, reverse
    entity_type = Column(String, nullable=False)
    entity_id = Column(String)
    old_values = Column(Text)  # JSON
    new_values = Column(Text)  # JSON
    ip_address = Column(String)
    session_id = Column(String)
    checksum = Column(String(64))  # SHA-256 hash for integrity
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def calculate_checksum(self):
        """Calculate SHA-256 checksum for integrity verification"""
        data = {
            'user_id': self.user_id,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        content = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def save(self, *args, **kwargs):
        """Override save to calculate checksum before saving"""
        if not self.checksum:
            self.checksum = self.calculate_checksum()
        super().save(*args, **kwargs)
