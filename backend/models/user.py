"""
User Model
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# User roles association table
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', String, ForeignKey('users.id')),
    Column('role_id', String, ForeignKey('roles.id'))
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    first_name_ar = Column(String)
    first_name_en = Column(String)
    last_name_ar = Column(String)
    last_name_en = Column(String)
    phone = Column(String)
    is_active = Column(Boolean, default=True)
    is_super_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    
    @property
    def full_name_ar(self):
        return f"{self.first_name_ar or ''} {self.last_name_ar or ''}".strip()
    
    @property
    def full_name_en(self):
        return f"{self.first_name_en or ''} {self.last_name_en or ''}".strip()
    
    def has_permission(self, permission_code: str) -> bool:
        """Check if user has a specific permission"""
        if self.is_super_admin:
            return True
        for role in self.roles:
            for permission in role.permissions:
                if permission.code == permission_code:
                    return True
        return False
