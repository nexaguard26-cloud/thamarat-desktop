"""
Audit Log Routes
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from models.database import get_db
from models.audit import AuditLog
from routes.auth import get_current_user, User

router = APIRouter()

@router.get("/logs")
async def get_audit_logs(
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get audit logs with filters"""
    query = db.query(AuditLog)
    
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)
    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)
    
    total = query.count()
    logs = query.order_by(AuditLog.created_at.desc())\
        .offset((page - 1) * limit).limit(limit).all()
    
    return {
        'data': logs,
        'meta': {
            'total': total,
            'page': page,
            'limit': limit,
            'total_pages': (total + limit - 1) // limit
        }
    }

@router.get("/verify")
async def verify_audit_integrity(
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Verify audit log integrity using checksums"""
    logs = db.query(AuditLog).filter(
        AuditLog.created_at >= start_date,
        AuditLog.created_at <= end_date
    ).all()
    
    tampered = []
    valid = []
    
    for log in logs:
        # Recalculate checksum
        test_log = AuditLog(
            user_id=log.user_id,
            action=log.action,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            old_values=log.old_values,
            new_values=log.new_values,
            created_at=log.created_at
        )
        expected_checksum = test_log.calculate_checksum()
        
        if expected_checksum != log.checksum:
            tampered.append({
                'id': log.id,
                'action': log.action,
                'entity_type': log.entity_type,
                'entity_id': log.entity_id,
                'created_at': log.created_at
            })
        else:
            valid.append(log.id)
    
    return {
        'valid': len(tampered) == 0,
        'total_logs': len(logs),
        'valid_logs': len(valid),
        'tampered_logs': len(tampered),
        'tampered_details': tampered,
        'verified_at': datetime.utcnow()
    }

@router.get("/entity/{entity_type}/{entity_id}")
async def get_entity_audit_trail(
    entity_type: str,
    entity_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get complete audit trail for a specific entity"""
    logs = db.query(AuditLog).filter(
        AuditLog.entity_type == entity_type,
        AuditLog.entity_id == entity_id
    ).order_by(AuditLog.created_at.desc()).all()
    
    return {
        'entity_type': entity_type,
        'entity_id': entity_id,
        'total_changes': len(logs),
        'changes': logs
    }
