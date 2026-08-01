"""
Audit logging utility
"""

import json
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from models.audit import AuditLog

def log_audit(
    db: Session,
    user_id: str,
    action: str,
    entity_type: str,
    entity_id: str = None,
    old_values: dict = None,
    new_values: dict = None,
    ip_address: str = None,
    session_id: str = None
):
    """Log an audit event"""
    try:
        audit_log = AuditLog(
            id=str(uuid.uuid4()),
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=json.dumps(old_values) if old_values else None,
            new_values=json.dumps(new_values) if new_values else None,
            ip_address=ip_address,
            session_id=session_id,
            created_at=datetime.utcnow()
        )
        
        # Calculate checksum before saving
        audit_log.checksum = audit_log.calculate_checksum()
        
        db.add(audit_log)
        db.commit()
        
        return audit_log
    except Exception as e:
        # Don't fail the main operation if audit logging fails
        print(f"Audit logging failed: {e}")
        db.rollback()
        return None
