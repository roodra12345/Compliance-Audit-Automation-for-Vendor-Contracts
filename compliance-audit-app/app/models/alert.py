from datetime import datetime
from app import db

class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # 'expiration', 'renewal', 'audit_due', 'high_risk', 'non_compliance'
    severity = db.Column(db.String(20), default='medium')  # 'low', 'medium', 'high', 'critical'
    title = db.Column(db.String(300), nullable=False)
    message = db.Column(db.Text, nullable=False)
    trigger_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_sent = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime)
    acknowledged = db.Column(db.Boolean, default=False)
    acknowledged_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    acknowledged_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    acknowledger = db.relationship('User', foreign_keys=[acknowledged_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'contract_id': self.contract_id,
            'contract': self.contract.contract_number if self.contract else None,
            'vendor': self.contract.vendor_name if self.contract else None,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'title': self.title,
            'message': self.message,
            'trigger_date': self.trigger_date.isoformat() if self.trigger_date else None,
            'is_active': self.is_active,
            'is_sent': self.is_sent,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'acknowledged': self.acknowledged,
            'acknowledged_by': self.acknowledger.username if self.acknowledger else None,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Alert {self.alert_type}: {self.title}>'