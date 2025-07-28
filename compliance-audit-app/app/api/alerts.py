from datetime import datetime
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Alert, Contract
from app.api import alerts_bp
from app.utils.audit_logger import log_action

@alerts_bp.route('/', methods=['GET'])
@jwt_required()
def get_alerts():
    """Get all alerts with optional filtering"""
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    is_active = request.args.get('is_active', type=bool)
    alert_type = request.args.get('alert_type')
    severity = request.args.get('severity')
    acknowledged = request.args.get('acknowledged', type=bool)
    
    # Build query
    query = Alert.query
    
    if is_active is not None:
        query = query.filter_by(is_active=is_active)
    if alert_type:
        query = query.filter_by(alert_type=alert_type)
    if severity:
        query = query.filter_by(severity=severity)
    if acknowledged is not None:
        query = query.filter_by(acknowledged=acknowledged)
    
    # Order by severity and trigger date
    query = query.order_by(
        db.case(
            (Alert.severity == 'critical', 1),
            (Alert.severity == 'high', 2),
            (Alert.severity == 'medium', 3),
            (Alert.severity == 'low', 4),
            else_=5
        ),
        Alert.trigger_date.desc()
    )
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    alerts = [alert.to_dict() for alert in pagination.items]
    
    return jsonify({
        'alerts': alerts,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@alerts_bp.route('/<int:alert_id>', methods=['GET'])
@jwt_required()
def get_alert(alert_id):
    """Get a specific alert"""
    alert = Alert.query.get_or_404(alert_id)
    return jsonify({'alert': alert.to_dict()}), 200

@alerts_bp.route('/<int:alert_id>/acknowledge', methods=['POST'])
@jwt_required()
def acknowledge_alert(alert_id):
    """Acknowledge an alert"""
    current_user_id = get_jwt_identity()
    alert = Alert.query.get_or_404(alert_id)
    
    if alert.acknowledged:
        return jsonify({'message': 'Alert already acknowledged'}), 200
    
    alert.acknowledged = True
    alert.acknowledged_by = current_user_id
    alert.acknowledged_at = datetime.utcnow()
    
    db.session.commit()
    
    # Log action
    log_action(current_user_id, 'acknowledge', 'alert', alert.id, {
        'alert_type': alert.alert_type,
        'severity': alert.severity
    })
    
    return jsonify({
        'message': 'Alert acknowledged successfully',
        'alert': alert.to_dict()
    }), 200

@alerts_bp.route('/<int:alert_id>/dismiss', methods=['POST'])
@jwt_required()
def dismiss_alert(alert_id):
    """Dismiss (deactivate) an alert"""
    current_user_id = get_jwt_identity()
    alert = Alert.query.get_or_404(alert_id)
    
    alert.is_active = False
    db.session.commit()
    
    # Log action
    log_action(current_user_id, 'dismiss', 'alert', alert.id, {
        'alert_type': alert.alert_type
    })
    
    return jsonify({
        'message': 'Alert dismissed successfully',
        'alert': alert.to_dict()
    }), 200

@alerts_bp.route('/active-count', methods=['GET'])
@jwt_required()
def get_active_alerts_count():
    """Get count of active alerts by severity"""
    counts = db.session.query(
        Alert.severity,
        db.func.count(Alert.id)
    ).filter(
        Alert.is_active == True,
        Alert.acknowledged == False
    ).group_by(Alert.severity).all()
    
    result = {
        'total': sum(count for _, count in counts),
        'by_severity': dict(counts)
    }
    
    return jsonify(result), 200

@alerts_bp.route('/upcoming', methods=['GET'])
@jwt_required()
def get_upcoming_alerts():
    """Get alerts scheduled for the next 7 days"""
    from datetime import timedelta
    
    end_date = datetime.utcnow() + timedelta(days=7)
    
    alerts = Alert.query.filter(
        Alert.trigger_date <= end_date,
        Alert.is_active == True,
        Alert.is_sent == False
    ).order_by(Alert.trigger_date.asc()).all()
    
    return jsonify({
        'alerts': [alert.to_dict() for alert in alerts],
        'total': len(alerts)
    }), 200

@alerts_bp.route('/contract/<int:contract_id>', methods=['GET'])
@jwt_required()
def get_contract_alerts(contract_id):
    """Get all alerts for a specific contract"""
    contract = Contract.query.get_or_404(contract_id)
    
    alerts = Alert.query.filter_by(contract_id=contract_id).order_by(
        Alert.trigger_date.desc()
    ).all()
    
    return jsonify({
        'alerts': [alert.to_dict() for alert in alerts],
        'total': len(alerts),
        'contract': {
            'id': contract.id,
            'contract_number': contract.contract_number,
            'vendor_name': contract.vendor_name
        }
    }), 200