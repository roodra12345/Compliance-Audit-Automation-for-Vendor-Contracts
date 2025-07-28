from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Contract
from app.api import chat_bp
from app.services import AIService
from app.utils.audit_logger import log_action

@chat_bp.route('/ask', methods=['POST'])
@jwt_required()
def ask_question():
    """Ask a natural language question about a contract"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('contract_id') or not data.get('question'):
        return jsonify({'error': 'contract_id and question are required'}), 400
    
    contract = Contract.query.get_or_404(data['contract_id'])
    
    if not contract.extracted_text:
        return jsonify({'error': 'Contract text not available'}), 400
    
    # Initialize AI service
    ai_service = AIService(
        current_app.config.get('AZURE_OPENAI_ENDPOINT'),
        current_app.config.get('AZURE_OPENAI_KEY'),
        current_app.config.get('AZURE_OPENAI_DEPLOYMENT_NAME')
    )
    
    # Get answer
    answer = ai_service.answer_contract_question(
        contract.extracted_text,
        data['question']
    )
    
    # Log action
    log_action(current_user_id, 'chat_query', 'contract', contract.id, {
        'question': data['question'][:200]  # Limit logged question length
    })
    
    return jsonify({
        'question': data['question'],
        'answer': answer,
        'contract': {
            'id': contract.id,
            'contract_number': contract.contract_number,
            'vendor_name': contract.vendor_name
        }
    }), 200

@chat_bp.route('/contract/<int:contract_id>/summary', methods=['GET'])
@jwt_required()
def get_contract_summary(contract_id):
    """Get an AI-generated summary of a contract"""
    current_user_id = get_jwt_identity()
    contract = Contract.query.get_or_404(contract_id)
    
    if not contract.extracted_text:
        return jsonify({'error': 'Contract text not available'}), 400
    
    # Initialize AI service
    ai_service = AIService(
        current_app.config.get('AZURE_OPENAI_ENDPOINT'),
        current_app.config.get('AZURE_OPENAI_KEY'),
        current_app.config.get('AZURE_OPENAI_DEPLOYMENT_NAME')
    )
    
    # Get summary
    summary = ai_service.summarize_contract(contract.extracted_text)
    
    # Log action
    log_action(current_user_id, 'generate_summary', 'contract', contract.id, {})
    
    return jsonify({
        'summary': summary,
        'contract': {
            'id': contract.id,
            'contract_number': contract.contract_number,
            'vendor_name': contract.vendor_name,
            'title': contract.title
        }
    }), 200

@chat_bp.route('/suggested-questions', methods=['GET'])
@jwt_required()
def get_suggested_questions():
    """Get suggested questions for contracts"""
    contract_id = request.args.get('contract_id', type=int)
    
    # General suggested questions
    general_questions = [
        "What are the key deliverables in this contract?",
        "What are the payment terms?",
        "Are there any penalty clauses?",
        "What are the termination conditions?",
        "What compliance standards does this contract require?",
        "What are the renewal terms?",
        "Are there any confidentiality requirements?",
        "What are the warranty provisions?"
    ]
    
    # Contract-specific questions
    specific_questions = []
    
    if contract_id:
        contract = Contract.query.get_or_404(contract_id)
        
        # Add vendor-specific questions
        specific_questions.append(f"What are {contract.vendor_name}'s obligations?")
        specific_questions.append(f"Does {contract.vendor_name} meet ISO requirements?")
        
        # Add questions based on detected clauses
        if contract.clauses.filter_by(clause_type='regulatory').first():
            specific_questions.append("What regulatory standards must be met?")
            specific_questions.append("Are there FDA compliance requirements?")
        
        if contract.clauses.filter_by(clause_type='penalty').first():
            specific_questions.append("What triggers penalty clauses?")
            specific_questions.append("What are the penalty amounts?")
        
        if contract.clauses.filter_by(clause_type='financial').first():
            specific_questions.append("What is the total contract value?")
            specific_questions.append("What are the payment milestones?")
    
    return jsonify({
        'general_questions': general_questions,
        'specific_questions': specific_questions
    }), 200

@chat_bp.route('/compliance-check', methods=['POST'])
@jwt_required()
def check_compliance():
    """Check if a contract meets specific compliance requirements"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('contract_id') or not data.get('standard'):
        return jsonify({'error': 'contract_id and standard are required'}), 400
    
    contract = Contract.query.get_or_404(data['contract_id'])
    standard = data['standard']  # e.g., 'ISO 13485', 'FDA', 'GDP', 'GMP'
    
    # Check if we have clauses related to this standard
    from app.models import Clause
    related_clauses = Clause.query.filter(
        Clause.contract_id == contract.id,
        db.or_(
            Clause.clause_subtype == standard,
            Clause.content.ilike(f'%{standard}%')
        )
    ).all()
    
    # Prepare response
    result = {
        'standard': standard,
        'has_requirements': len(related_clauses) > 0,
        'related_clauses': [clause.to_dict() for clause in related_clauses],
        'contract': {
            'id': contract.id,
            'contract_number': contract.contract_number,
            'vendor_name': contract.vendor_name
        }
    }
    
    # If we have AI service, get a more detailed analysis
    if contract.extracted_text:
        ai_service = AIService(
            current_app.config.get('AZURE_OPENAI_ENDPOINT'),
            current_app.config.get('AZURE_OPENAI_KEY'),
            current_app.config.get('AZURE_OPENAI_DEPLOYMENT_NAME')
        )
        
        question = f"Does this contract contain requirements for {standard} compliance? If yes, what are they?"
        answer = ai_service.answer_contract_question(contract.extracted_text, question)
        result['ai_analysis'] = answer
    
    # Log action
    log_action(current_user_id, 'compliance_check', 'contract', contract.id, {
        'standard': standard
    })
    
    return jsonify(result), 200