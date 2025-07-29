import os
import uuid
from datetime import datetime, date
from flask import request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app import db
from app.models import Contract, Clause, User
from app.api import contracts_bp
from app.services import OCRService, AIService
from app.utils.audit_logger import log_action

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@contracts_bp.route('/', methods=['GET'])
@jwt_required()
def get_contracts():
    """Get all contracts with optional filtering"""
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
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
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    contracts = []
    for contract in pagination.items:
        contract_dict = contract.to_dict()
        contract_dict['clauses_count'] = contract.clauses.count()
        contracts.append(contract_dict)
    
    return jsonify({
        'contracts': contracts,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@contracts_bp.route('/<int:contract_id>', methods=['GET'])
@jwt_required()
def get_contract(contract_id):
    """Get a specific contract with its clauses"""
    contract = Contract.query.get_or_404(contract_id)
    
    contract_dict = contract.to_dict()
    contract_dict['clauses'] = [clause.to_dict() for clause in contract.clauses]
    
    return jsonify({'contract': contract_dict}), 200

@contracts_bp.route('/', methods=['POST'])
@jwt_required()
def create_contract():
    """Upload and process a new contract"""
    current_user_id = get_jwt_identity()
    
    # Check if file is present
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only PDF files are allowed'}), 400
    
    # Get form data
    vendor_name = request.form.get('vendor_name', 'Unknown Vendor')
    contract_number = request.form.get('contract_number', f'AUTO-{uuid.uuid4().hex[:8].upper()}')
    title = request.form.get('title', 'Untitled Contract')
    
    # Check if contract number already exists
    if Contract.query.filter_by(contract_number=contract_number).first():
        return jsonify({'error': 'Contract number already exists'}), 400
    
    try:
        # Save file
        original_filename = secure_filename(file.filename)
        stored_filename = f"{uuid.uuid4().hex}_{original_filename}"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], stored_filename)
        file.save(file_path)
        
        # Extract text using OCR service
        ocr_service = OCRService(
            current_app.config.get('AZURE_COMPUTER_VISION_ENDPOINT'),
            current_app.config.get('AZURE_COMPUTER_VISION_KEY')
        )
        
        ocr_result = ocr_service.extract_text_from_pdf(file_path)
        
        if not ocr_result['success']:
            return jsonify({'error': f"OCR failed: {ocr_result['error']}"}), 500
        
        # Create contract record
        contract = Contract(
            vendor_name=vendor_name,
            contract_number=contract_number,
            title=title,
            original_filename=original_filename,
            stored_filename=stored_filename,
            extracted_text=ocr_result['text'],
            owner_id=current_user_id
        )
        
        db.session.add(contract)
        db.session.flush()  # Get contract ID without committing
        
        # Analyze contract using AI service
        ai_service = AIService(
            current_app.config.get('AZURE_OPENAI_ENDPOINT'),
            current_app.config.get('AZURE_OPENAI_KEY'),
            current_app.config.get('AZURE_OPENAI_DEPLOYMENT_NAME')
        )
        
        ai_result = ai_service.analyze_contract(ocr_result['text'])
        
        if ai_result.get('success'):
            # Update contract with AI-extracted metadata
            metadata = ai_result.get('metadata', {})
            if metadata.get('start_date'):
                try:
                    contract.start_date = datetime.strptime(metadata['start_date'], '%Y-%m-%d').date()
                except:
                    pass
            
            if metadata.get('end_date'):
                try:
                    contract.end_date = datetime.strptime(metadata['end_date'], '%Y-%m-%d').date()
                except:
                    pass
            
            if metadata.get('contract_value'):
                try:
                    contract.contract_value = float(metadata['contract_value'])
                except:
                    pass
            
            if metadata.get('currency'):
                contract.currency = metadata['currency']
            
            # Set risk level based on AI assessment
            risk_assessment = ai_result.get('risk_assessment', {})
            contract.risk_level = risk_assessment.get('overall_risk', 'medium')
            
            # Create clause records
            for clause_data in ai_result.get('clauses', []):
                clause = Clause(
                    contract_id=contract.id,
                    clause_type=clause_data.get('clause_type', 'other'),
                    clause_subtype=clause_data.get('clause_subtype'),
                    title=clause_data.get('title', 'Untitled Clause'),
                    content=clause_data.get('content', '')[:1000],  # Limit content length
                    summary=clause_data.get('summary'),
                    compliance_requirement=clause_data.get('compliance_requirement'),
                    risk_assessment=clause_data.get('risk_assessment', 'medium'),
                    action_required=clause_data.get('action_required', False),
                    financial_amount=clause_data.get('financial_amount'),
                    penalty_amount=clause_data.get('penalty_amount'),
                    penalty_trigger=clause_data.get('penalty_trigger')
                )
                db.session.add(clause)
        
        db.session.commit()
        
        # Log action
        log_action(current_user_id, 'upload', 'contract', contract.id, {
            'filename': original_filename,
            'vendor': vendor_name,
            'contract_number': contract_number
        })
        
        contract_dict = contract.to_dict()
        contract_dict['ocr_method'] = ocr_result['method']
        contract_dict['ai_analysis'] = ai_result.get('success', False)
        
        return jsonify({
            'message': 'Contract uploaded and processed successfully',
            'contract': contract_dict
        }), 201
        
    except Exception as e:
        db.session.rollback()
        # Clean up uploaded file on error
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@contracts_bp.route('/<int:contract_id>', methods=['PUT'])
@jwt_required()
def update_contract(contract_id):
    """Update contract information"""
    current_user_id = get_jwt_identity()
    contract = Contract.query.get_or_404(contract_id)
    
    data = request.get_json()
    
    # Update allowed fields
    if 'vendor_name' in data:
        contract.vendor_name = data['vendor_name']
    if 'title' in data:
        contract.title = data['title']
    if 'risk_level' in data:
        contract.risk_level = data['risk_level']
    if 'compliance_status' in data:
        contract.compliance_status = data['compliance_status']
    if 'start_date' in data:
        try:
            contract.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        except:
            pass
    if 'end_date' in data:
        try:
            contract.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        except:
            pass
    if 'contract_value' in data:
        try:
            contract.contract_value = float(data['contract_value'])
        except:
            pass
    
    contract.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Log action
    log_action(current_user_id, 'update', 'contract', contract.id, data)
    
    return jsonify({
        'message': 'Contract updated successfully',
        'contract': contract.to_dict()
    }), 200

@contracts_bp.route('/<int:contract_id>', methods=['DELETE'])
@jwt_required()
def delete_contract(contract_id):
    """Delete a contract"""
    current_user_id = get_jwt_identity()
    contract = Contract.query.get_or_404(contract_id)
    
    # Delete file
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], contract.stored_filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Log action before deletion
    log_action(current_user_id, 'delete', 'contract', contract.id, {
        'contract_number': contract.contract_number,
        'vendor': contract.vendor_name
    })
    
    db.session.delete(contract)
    db.session.commit()
    
    return jsonify({'message': 'Contract deleted successfully'}), 200

@contracts_bp.route('/<int:contract_id>/download', methods=['GET'])
@jwt_required()
def download_contract(contract_id):
    """Download original contract file"""
    current_user_id = get_jwt_identity()
    contract = Contract.query.get_or_404(contract_id)
    
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], contract.stored_filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    # Log action
    log_action(current_user_id, 'download', 'contract', contract.id, {
        'filename': contract.original_filename
    })
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=contract.original_filename,
        mimetype='application/pdf'
    )

@contracts_bp.route('/<int:contract_id>/audit', methods=['POST'])
@jwt_required()
def mark_audited(contract_id):
    """Mark contract as audited"""
    current_user_id = get_jwt_identity()
    contract = Contract.query.get_or_404(contract_id)
    
    contract.last_audit_date = datetime.utcnow()
    contract.compliance_status = 'compliant'  # Can be updated based on audit results
    
    # Calculate next audit date based on risk level
    from datetime import timedelta
    if contract.risk_level == 'high':
        contract.next_audit_date = datetime.utcnow() + timedelta(days=90)
    elif contract.risk_level == 'medium':
        contract.next_audit_date = datetime.utcnow() + timedelta(days=180)
    else:
        contract.next_audit_date = datetime.utcnow() + timedelta(days=365)
    
    db.session.commit()
    
    # Log action
    log_action(current_user_id, 'audit', 'contract', contract.id, {
        'compliance_status': contract.compliance_status,
        'next_audit_date': contract.next_audit_date.isoformat()
    })
    
    return jsonify({
        'message': 'Contract marked as audited',
        'contract': contract.to_dict()
    }), 200