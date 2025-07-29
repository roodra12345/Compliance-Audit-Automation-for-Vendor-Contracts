from datetime import datetime
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Clause, Contract
from app.api import clauses_bp
from app.utils.audit_logger import log_action

@clauses_bp.route('/', methods=['GET'])
@jwt_required()
def get_clauses():
    """Get all clauses with optional filtering"""
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    contract_id = request.args.get('contract_id', type=int)
    clause_type = request.args.get('clause_type')
    risk_assessment = request.args.get('risk_assessment')
    action_required = request.args.get('action_required', type=bool)
    
    # Build query
    query = Clause.query
    
    if contract_id:
        query = query.filter_by(contract_id=contract_id)
    if clause_type:
        query = query.filter_by(clause_type=clause_type)
    if risk_assessment:
        query = query.filter_by(risk_assessment=risk_assessment)
    if action_required is not None:
        query = query.filter_by(action_required=action_required)
    
    # Order by risk assessment (high risk first)
    query = query.order_by(
        db.case(
            (Clause.risk_assessment == 'high', 1),
            (Clause.risk_assessment == 'medium', 2),
            (Clause.risk_assessment == 'low', 3),
            else_=4
        )
    )
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    clauses = []
    for clause in pagination.items:
        clause_dict = clause.to_dict()
        # Add contract info
        if clause.contract:
            clause_dict['contract_number'] = clause.contract.contract_number
            clause_dict['vendor_name'] = clause.contract.vendor_name
        clauses.append(clause_dict)
    
    return jsonify({
        'clauses': clauses,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@clauses_bp.route('/<int:clause_id>', methods=['GET'])
@jwt_required()
def get_clause(clause_id):
    """Get a specific clause"""
    clause = Clause.query.get_or_404(clause_id)
    
    clause_dict = clause.to_dict()
    # Add contract info
    if clause.contract:
        clause_dict['contract'] = {
            'id': clause.contract.id,
            'contract_number': clause.contract.contract_number,
            'vendor_name': clause.contract.vendor_name,
            'title': clause.contract.title
        }
    
    return jsonify({'clause': clause_dict}), 200

@clauses_bp.route('/<int:clause_id>', methods=['PUT'])
@jwt_required()
def update_clause(clause_id):
    """Update clause information"""
    current_user_id = get_jwt_identity()
    clause = Clause.query.get_or_404(clause_id)
    
    data = request.get_json()
    
    # Update allowed fields
    if 'title' in data:
        clause.title = data['title']
    if 'summary' in data:
        clause.summary = data['summary']
    if 'risk_assessment' in data:
        clause.risk_assessment = data['risk_assessment']
    if 'action_required' in data:
        clause.action_required = data['action_required']
    if 'action_deadline' in data:
        try:
            clause.action_deadline = datetime.strptime(data['action_deadline'], '%Y-%m-%d').date()
        except:
            clause.action_deadline = None
    if 'compliance_requirement' in data:
        clause.compliance_requirement = data['compliance_requirement']
    
    db.session.commit()
    
    # Log action
    log_action(current_user_id, 'update', 'clause', clause.id, data)
    
    return jsonify({
        'message': 'Clause updated successfully',
        'clause': clause.to_dict()
    }), 200

@clauses_bp.route('/<int:clause_id>/review', methods=['POST'])
@jwt_required()
def review_clause(clause_id):
    """Mark clause as reviewed"""
    current_user_id = get_jwt_identity()
    clause = Clause.query.get_or_404(clause_id)
    
    clause.reviewed = True
    clause.reviewed_at = datetime.utcnow()
    clause.reviewed_by = current_user_id
    
    db.session.commit()
    
    # Log action
    log_action(current_user_id, 'review', 'clause', clause.id, {
        'clause_type': clause.clause_type,
        'risk_assessment': clause.risk_assessment
    })
    
    return jsonify({
        'message': 'Clause marked as reviewed',
        'clause': clause.to_dict()
    }), 200

@clauses_bp.route('/types', methods=['GET'])
@jwt_required()
def get_clause_types():
    """Get all available clause types and subtypes"""
    # Get distinct clause types
    clause_types = db.session.query(Clause.clause_type).distinct().all()
    clause_types = [ct[0] for ct in clause_types if ct[0]]
    
    # Get subtypes for each type
    type_subtypes = {}
    for clause_type in clause_types:
        subtypes = db.session.query(Clause.clause_subtype).filter(
            Clause.clause_type == clause_type,
            Clause.clause_subtype.isnot(None)
        ).distinct().all()
        type_subtypes[clause_type] = [st[0] for st in subtypes if st[0]]
    
    return jsonify({
        'clause_types': clause_types,
        'type_subtypes': type_subtypes
    }), 200

@clauses_bp.route('/action-required', methods=['GET'])
@jwt_required()
def get_action_required_clauses():
    """Get all clauses requiring action"""
    # Get clauses with action_required = True
    clauses = Clause.query.filter_by(action_required=True).order_by(
        Clause.action_deadline.asc(),
        db.case(
            (Clause.risk_assessment == 'high', 1),
            (Clause.risk_assessment == 'medium', 2),
            (Clause.risk_assessment == 'low', 3),
            else_=4
        )
    ).all()
    
    result = []
    for clause in clauses:
        clause_dict = clause.to_dict()
        # Add contract info
        if clause.contract:
            clause_dict['contract_number'] = clause.contract.contract_number
            clause_dict['vendor_name'] = clause.contract.vendor_name
        
        # Calculate days until deadline
        if clause.action_deadline:
            days_until_deadline = (clause.action_deadline - datetime.utcnow().date()).days
            clause_dict['days_until_deadline'] = days_until_deadline
        
        result.append(clause_dict)
    
    return jsonify({
        'clauses': result,
        'total': len(result)
    }), 200