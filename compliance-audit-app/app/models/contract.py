from datetime import datetime
from app import db

class Contract(db.Model):
    __tablename__ = 'contracts'
    
    id = db.Column(db.Integer, primary_key=True)
    vendor_name = db.Column(db.String(200), nullable=False)
    contract_number = db.Column(db.String(100), unique=True, nullable=False)
    title = db.Column(db.String(300), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    extracted_text = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    renewal_date = db.Column(db.Date)
    contract_value = db.Column(db.Numeric(12, 2))
    currency = db.Column(db.String(3), default='USD')
    risk_level = db.Column(db.String(20), default='medium')  # 'low', 'medium', 'high'
    compliance_status = db.Column(db.String(20), default='pending')  # 'pending', 'compliant', 'non_compliant', 'review_required'
    last_audit_date = db.Column(db.DateTime)
    next_audit_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    clauses = db.relationship('Clause', backref='contract', lazy='dynamic', cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', backref='contract', lazy='dynamic')
    alerts = db.relationship('Alert', backref='contract', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'vendor_name': self.vendor_name,
            'contract_number': self.contract_number,
            'title': self.title,
            'original_filename': self.original_filename,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'renewal_date': self.renewal_date.isoformat() if self.renewal_date else None,
            'contract_value': float(self.contract_value) if self.contract_value else None,
            'currency': self.currency,
            'risk_level': self.risk_level,
            'compliance_status': self.compliance_status,
            'last_audit_date': self.last_audit_date.isoformat() if self.last_audit_date else None,
            'next_audit_date': self.next_audit_date.isoformat() if self.next_audit_date else None,
            'owner': self.owner.username if self.owner else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'clauses_count': self.clauses.count()
        }
    
    def __repr__(self):
        return f'<Contract {self.contract_number}: {self.vendor_name}>'