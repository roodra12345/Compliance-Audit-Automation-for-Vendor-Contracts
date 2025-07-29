from datetime import datetime
from app import db

class Clause(db.Model):
    __tablename__ = 'clauses'
    
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'), nullable=False)
    clause_type = db.Column(db.String(100), nullable=False)  # 'regulatory', 'financial', 'penalty', 'renewal', 'termination', 'other'
    clause_subtype = db.Column(db.String(100))  # 'ISO', 'FDA', 'GDP', 'GMP', etc.
    title = db.Column(db.String(300), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text)
    page_number = db.Column(db.Integer)
    section_reference = db.Column(db.String(100))
    compliance_requirement = db.Column(db.Text)
    risk_assessment = db.Column(db.String(20), default='medium')  # 'low', 'medium', 'high'
    action_required = db.Column(db.Boolean, default=False)
    action_deadline = db.Column(db.Date)
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed = db.Column(db.Boolean, default=False)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Financial specific fields
    financial_amount = db.Column(db.Numeric(12, 2))
    financial_currency = db.Column(db.String(3))
    payment_terms = db.Column(db.String(200))
    
    # Penalty specific fields
    penalty_amount = db.Column(db.Numeric(12, 2))
    penalty_trigger = db.Column(db.Text)
    
    # Relationships
    reviewer = db.relationship('User', foreign_keys=[reviewed_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'contract_id': self.contract_id,
            'clause_type': self.clause_type,
            'clause_subtype': self.clause_subtype,
            'title': self.title,
            'content': self.content,
            'summary': self.summary,
            'page_number': self.page_number,
            'section_reference': self.section_reference,
            'compliance_requirement': self.compliance_requirement,
            'risk_assessment': self.risk_assessment,
            'action_required': self.action_required,
            'action_deadline': self.action_deadline.isoformat() if self.action_deadline else None,
            'detected_at': self.detected_at.isoformat() if self.detected_at else None,
            'reviewed': self.reviewed,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'reviewed_by': self.reviewer.username if self.reviewer else None,
            'financial_amount': float(self.financial_amount) if self.financial_amount else None,
            'financial_currency': self.financial_currency,
            'payment_terms': self.payment_terms,
            'penalty_amount': float(self.penalty_amount) if self.penalty_amount else None,
            'penalty_trigger': self.penalty_trigger
        }
    
    def __repr__(self):
        return f'<Clause {self.clause_type}: {self.title}>'