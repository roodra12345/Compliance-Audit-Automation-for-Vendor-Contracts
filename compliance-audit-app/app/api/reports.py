from flask import request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Contract, Clause
from app.api import reports_bp
from app.services import ReportService
from app.utils.audit_logger import log_action

@reports_bp.route('/contracts/csv', methods=['GET'])
@jwt_required()
def export_contracts_csv():
    """Export contracts data as CSV"""
    current_user_id = get_jwt_identity()
    
    # Get query parameters for filtering
    vendor_name = request.args.get('vendor_name')
    risk_level = request.args.get('risk_level')
    compliance_status = request.args.get('compliance_status')
    
    # Build query
    query = Contract.query
    
    if vendor_name:
        query = query.filter(Contract.vendor_name.ilike(f'%{vendor_name}%'))
    if risk_level:
        query = query.filter_by(risk_level=risk_level)
    if compliance_status:
        query = query.filter_by(compliance_status=compliance_status)
    
    contracts = query.all()
    
    # Convert to dict format with clauses
    contracts_data = []
    for contract in contracts:
        contract_dict = contract.to_dict()
        contract_dict['clauses'] = [clause.to_dict() for clause in contract.clauses]
        contracts_data.append(contract_dict)
    
    # Generate CSV
    report_service = ReportService()
    csv_buffer = report_service.generate_contract_report_csv(contracts_data)
    
    # Log action
    log_action(current_user_id, 'export', 'report', None, {
        'report_type': 'contracts_csv',
        'count': len(contracts)
    })
    
    return send_file(
        csv_buffer,
        mimetype='text/csv',
        as_attachment=True,
        download_name='contracts_report.csv'
    )

@reports_bp.route('/clauses/csv', methods=['GET'])
@jwt_required()
def export_clauses_csv():
    """Export clauses data as CSV"""
    current_user_id = get_jwt_identity()
    
    # Get query parameters for filtering
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
    
    clauses = query.all()
    
    # Convert to dict format with contract info
    clauses_data = []
    for clause in clauses:
        clause_dict = clause.to_dict()
        if clause.contract:
            clause_dict['contract_number'] = clause.contract.contract_number
            clause_dict['vendor_name'] = clause.contract.vendor_name
        clauses_data.append(clause_dict)
    
    # Generate CSV
    report_service = ReportService()
    csv_buffer = report_service.generate_clauses_report_csv(clauses_data)
    
    # Log action
    log_action(current_user_id, 'export', 'report', None, {
        'report_type': 'clauses_csv',
        'count': len(clauses)
    })
    
    return send_file(
        csv_buffer,
        mimetype='text/csv',
        as_attachment=True,
        download_name='clauses_report.csv'
    )

@reports_bp.route('/contract/<int:contract_id>/pdf', methods=['GET'])
@jwt_required()
def export_contract_pdf(contract_id):
    """Export single contract report as PDF"""
    current_user_id = get_jwt_identity()
    
    contract = Contract.query.get_or_404(contract_id)
    
    # Get contract data with clauses and risk assessment
    contract_dict = contract.to_dict()
    contract_dict['clauses'] = [clause.to_dict() for clause in contract.clauses]
    
    # Calculate risk assessment
    high_risk_clauses = sum(1 for clause in contract.clauses if clause.risk_assessment == 'high')
    medium_risk_clauses = sum(1 for clause in contract.clauses if clause.risk_assessment == 'medium')
    
    contract_dict['risk_assessment'] = {
        'overall_risk': contract.risk_level,
        'high_risk_clauses': high_risk_clauses,
        'medium_risk_clauses': medium_risk_clauses,
        'risk_factors': [],
        'recommendations': []
    }
    
    # Add risk factors
    if any(clause.clause_type == 'penalty' for clause in contract.clauses):
        contract_dict['risk_assessment']['risk_factors'].append('Contains penalty clauses')
    if any(clause.clause_type == 'regulatory' for clause in contract.clauses):
        contract_dict['risk_assessment']['risk_factors'].append('Subject to regulatory compliance')
    if any(clause.action_required for clause in contract.clauses):
        contract_dict['risk_assessment']['risk_factors'].append('Immediate action required for some clauses')
    
    # Add recommendations
    if contract.risk_level in ['high', 'medium']:
        contract_dict['risk_assessment']['recommendations'].append('Schedule detailed compliance review')
    if any(clause.clause_type == 'regulatory' for clause in contract.clauses):
        contract_dict['risk_assessment']['recommendations'].append('Ensure all regulatory requirements are met')
    
    # Generate PDF
    report_service = ReportService()
    pdf_buffer = report_service.generate_contract_report_pdf(contract_dict)
    
    # Log action
    log_action(current_user_id, 'export', 'report', contract_id, {
        'report_type': 'contract_pdf',
        'contract_number': contract.contract_number
    })
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'contract_report_{contract.contract_number}.pdf'
    )

@reports_bp.route('/compliance-summary/pdf', methods=['GET'])
@jwt_required()
def export_compliance_summary_pdf():
    """Export compliance summary report as PDF"""
    current_user_id = get_jwt_identity()
    
    # Get all contracts
    contracts = Contract.query.all()
    
    # Convert to dict format
    contracts_data = [contract.to_dict() for contract in contracts]
    
    # Generate PDF
    report_service = ReportService()
    pdf_buffer = report_service.generate_compliance_summary_pdf(contracts_data)
    
    # Log action
    log_action(current_user_id, 'export', 'report', None, {
        'report_type': 'compliance_summary_pdf',
        'count': len(contracts)
    })
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='compliance_summary_report.pdf'
    )

@reports_bp.route('/dashboard-stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get statistics for dashboard"""
    # Total contracts
    total_contracts = Contract.query.count()
    
    # Contracts by status
    contracts_by_status = db.session.query(
        Contract.compliance_status,
        db.func.count(Contract.id)
    ).group_by(Contract.compliance_status).all()
    
    # Contracts by risk level
    contracts_by_risk = db.session.query(
        Contract.risk_level,
        db.func.count(Contract.id)
    ).group_by(Contract.risk_level).all()
    
    # Clauses statistics
    total_clauses = Clause.query.count()
    high_risk_clauses = Clause.query.filter_by(risk_assessment='high').count()
    action_required_clauses = Clause.query.filter_by(action_required=True).count()
    
    # Upcoming audits (next 30 days)
    from datetime import datetime, timedelta
    upcoming_date = datetime.utcnow() + timedelta(days=30)
    upcoming_audits = Contract.query.filter(
        Contract.next_audit_date <= upcoming_date
    ).count()
    
    # Expiring contracts (next 90 days)
    expiring_date = datetime.utcnow().date() + timedelta(days=90)
    expiring_contracts = Contract.query.filter(
        Contract.end_date <= expiring_date
    ).count()
    
    return jsonify({
        'total_contracts': total_contracts,
        'contracts_by_status': dict(contracts_by_status),
        'contracts_by_risk': dict(contracts_by_risk),
        'total_clauses': total_clauses,
        'high_risk_clauses': high_risk_clauses,
        'action_required_clauses': action_required_clauses,
        'upcoming_audits': upcoming_audits,
        'expiring_contracts': expiring_contracts
    }), 200