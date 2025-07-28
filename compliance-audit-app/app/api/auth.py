from flask import request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app import db
from app.models import User, AuditLog
from app.api import auth_bp
from app.utils.audit_logger import log_action

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    # Validate input
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Check if user exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create new user
    user = User(
        username=data['username'],
        email=data['email'],
        role=data.get('role', 'auditor')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # Log action
    log_action(user.id, 'register', 'user', user.id, {'username': user.username})
    
    # Create tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    
    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400
    
    # Find user by username or email
    user = User.query.filter(
        (User.username == data['username']) | (User.email == data['username'])
    ).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is disabled'}), 401
    
    # Log action
    log_action(user.id, 'login', 'user', user.id, {
        'ip_address': request.remote_addr,
        'user_agent': request.headers.get('User-Agent')
    })
    
    # Create tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    current_user_id = get_jwt_identity()
    
    # Create new access token
    access_token = create_access_token(identity=current_user_id)
    
    return jsonify({'access_token': access_token}), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()}), 200

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Update allowed fields
    if 'email' in data:
        # Check if email already exists
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user.id:
            return jsonify({'error': 'Email already exists'}), 400
        user.email = data['email']
    
    if 'username' in data:
        # Check if username already exists
        existing = User.query.filter_by(username=data['username']).first()
        if existing and existing.id != user.id:
            return jsonify({'error': 'Username already exists'}), 400
        user.username = data['username']
    
    db.session.commit()
    
    # Log action
    log_action(user.id, 'update_profile', 'user', user.id, data)
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': user.to_dict()
    }), 200

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    if not data.get('old_password') or not data.get('new_password'):
        return jsonify({'error': 'Old and new passwords required'}), 400
    
    # Verify old password
    if not user.check_password(data['old_password']):
        return jsonify({'error': 'Invalid old password'}), 401
    
    # Set new password
    user.set_password(data['new_password'])
    db.session.commit()
    
    # Log action
    log_action(user.id, 'change_password', 'user', user.id, {})
    
    return jsonify({'message': 'Password changed successfully'}), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user"""
    current_user_id = get_jwt_identity()
    
    # Log action
    log_action(current_user_id, 'logout', 'user', current_user_id, {
        'ip_address': request.remote_addr
    })
    
    # In a real application, you might want to blacklist the token here
    
    return jsonify({'message': 'Logged out successfully'}), 200