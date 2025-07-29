from datetime import datetime, timedelta
from app import db
from app.models import Contract, Alert, User
from app.services import EmailService

def setup_scheduler(app, scheduler):
    """Setup scheduled tasks"""
    
    @scheduler.task('cron', id='check_contract_expiry', hour=9, minute=0)
    def check_contract_expiry():
        """Check for expiring contracts daily"""
        with app.app_context():
            # Check contracts expiring in 30, 60, and 90 days
            for days in [30, 60, 90]:
                expiry_date = datetime.utcnow().date() + timedelta(days=days)
                
                contracts = Contract.query.filter(
                    Contract.end_date == expiry_date
                ).all()
                
                for contract in contracts:
                    # Check if alert already exists
                    existing_alert = Alert.query.filter_by(
                        contract_id=contract.id,
                        alert_type='expiration',
                        trigger_date=datetime.utcnow().date()
                    ).first()
                    
                    if not existing_alert:
                        # Create alert
                        alert = Alert(
                            contract_id=contract.id,
                            alert_type='expiration',
                            severity='high' if days <= 30 else 'medium',
                            title=f'Contract Expiring in {days} Days',
                            message=f'Contract {contract.contract_number} with {contract.vendor_name} will expire on {contract.end_date}',
                            trigger_date=datetime.utcnow()
                        )
                        db.session.add(alert)
                        
                        # Send email notification
                        email_service = EmailService(app.extensions.get('mail'))
                        email_service.send_contract_expiration_notice(
                            contract.owner.email,
                            contract.to_dict(),
                            days
                        )
            
            db.session.commit()
    
    @scheduler.task('cron', id='check_audit_due', hour=9, minute=30)
    def check_audit_due():
        """Check for contracts due for audit"""
        with app.app_context():
            # Get contracts where next_audit_date is within 7 days
            due_date = datetime.utcnow() + timedelta(days=7)
            
            contracts = Contract.query.filter(
                Contract.next_audit_date <= due_date,
                Contract.next_audit_date >= datetime.utcnow()
            ).all()
            
            for contract in contracts:
                # Check if alert already exists
                existing_alert = Alert.query.filter_by(
                    contract_id=contract.id,
                    alert_type='audit_due',
                    trigger_date=datetime.utcnow().date()
                ).first()
                
                if not existing_alert:
                    days_until = (contract.next_audit_date - datetime.utcnow()).days
                    
                    # Create alert
                    alert = Alert(
                        contract_id=contract.id,
                        alert_type='audit_due',
                        severity='high' if days_until <= 3 else 'medium',
                        title=f'Audit Due in {days_until} Days',
                        message=f'Contract {contract.contract_number} with {contract.vendor_name} is due for compliance audit',
                        trigger_date=datetime.utcnow()
                    )
                    db.session.add(alert)
            
            db.session.commit()
    
    @scheduler.task('cron', id='check_high_risk_contracts', hour=10, minute=0)
    def check_high_risk_contracts():
        """Check high-risk contracts weekly (Monday)"""
        with app.app_context():
            if datetime.utcnow().weekday() == 0:  # Monday
                contracts = Contract.query.filter_by(
                    risk_level='high',
                    compliance_status='pending'
                ).all()
                
                for contract in contracts:
                    # Create weekly reminder for high-risk contracts
                    alert = Alert(
                        contract_id=contract.id,
                        alert_type='high_risk',
                        severity='high',
                        title='High Risk Contract Review Required',
                        message=f'High-risk contract {contract.contract_number} with {contract.vendor_name} requires review',
                        trigger_date=datetime.utcnow()
                    )
                    db.session.add(alert)
                
                db.session.commit()
    
    @scheduler.task('cron', id='send_daily_digest', hour=8, minute=0)
    def send_daily_digest():
        """Send daily digest of alerts to users"""
        with app.app_context():
            # Get all active users
            users = User.query.filter_by(is_active=True).all()
            
            email_service = EmailService(app.extensions.get('mail'))
            
            for user in users:
                # Get user's contracts
                user_contracts = Contract.query.filter_by(owner_id=user.id).all()
                
                if not user_contracts:
                    continue
                
                # Get contracts needing attention
                contracts_due_audit = []
                contracts_expiring = []
                
                for contract in user_contracts:
                    # Check audit due
                    if contract.next_audit_date:
                        days_until_audit = (contract.next_audit_date - datetime.utcnow()).days
                        if 0 <= days_until_audit <= 30:
                            contracts_due_audit.append(contract.to_dict())
                    
                    # Check expiring
                    if contract.end_date:
                        days_until_expiry = (contract.end_date - datetime.utcnow().date()).days
                        if 0 <= days_until_expiry <= 90:
                            contracts_expiring.append(contract.to_dict())
                
                # Send email if there are contracts needing attention
                if contracts_due_audit:
                    email_service.send_audit_reminder(user.email, contracts_due_audit)
    
    @scheduler.task('cron', id='process_pending_alerts', hour='*/1')
    def process_pending_alerts():
        """Process and send pending alerts every hour"""
        with app.app_context():
            # Get unsent alerts that should be triggered
            pending_alerts = Alert.query.filter(
                Alert.is_active == True,
                Alert.is_sent == False,
                Alert.trigger_date <= datetime.utcnow()
            ).all()
            
            email_service = EmailService(app.extensions.get('mail'))
            
            for alert in pending_alerts:
                # Send email notification
                if alert.contract and alert.contract.owner:
                    success = email_service.send_alert_email(
                        alert.contract.owner.email,
                        alert.to_dict()
                    )
                    
                    if success:
                        alert.is_sent = True
                        alert.sent_at = datetime.utcnow()
            
            db.session.commit()
    
    @scheduler.task('cron', id='cleanup_old_alerts', hour=2, minute=0)
    def cleanup_old_alerts():
        """Clean up old acknowledged alerts (older than 90 days)"""
        with app.app_context():
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            
            old_alerts = Alert.query.filter(
                Alert.acknowledged == True,
                Alert.acknowledged_at < cutoff_date
            ).all()
            
            for alert in old_alerts:
                alert.is_active = False
            
            db.session.commit()