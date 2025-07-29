from flask import request
from app import db
from app.models import AuditLog

def log_action(user_id, action, resource_type=None, resource_id=None, details=None):
    """Log user actions for audit trail"""
    try:
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=request.remote_addr if request else None,
            user_agent=request.headers.get('User-Agent') if request else None
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
    except Exception as e:
        print(f"Audit logging error: {e}")
        db.session.rollback()