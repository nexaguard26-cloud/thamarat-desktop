"""
Role and Permission Models
"""

from sqlalchemy import Column, String, Boolean, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# Role permissions association table
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', String, ForeignKey('roles.id')),
    Column('permission_id', String, ForeignKey('permissions.id'))
)

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    name_ar = Column(String)
    name_en = Column(String)
    description = Column(String)
    is_system_role = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", secondary="user_roles", back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions)

class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(String, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    name_ar = Column(String)
    name_en = Column(String)
    module = Column(String)  # gl, fund, budget, hr, admin
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    roles = relationship("Role", secondary=role_permissions)
