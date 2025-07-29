from datetime import datetime
from app import db

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'))
    action = db.Column(db.String(100), nullable=False)  # 'login', 'logout', 'upload', 'download', 'review', 'update', 'delete'
    resource_type = db.Column(db.String(50))  # 'contract', 'clause', 'user', 'report'
    resource_id = db.Column(db.Integer)
    details = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user.username if self.user else None,
            'contract_id': self.contract_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    def __repr__(self):
        return f'<AuditLog {self.action} by {self.user_id} at {self.timestamp}>'