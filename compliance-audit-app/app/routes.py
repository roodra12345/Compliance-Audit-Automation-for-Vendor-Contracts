from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Landing page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html')

@main_bp.route('/contracts')
@login_required
def contracts():
    """Contracts page"""
    return render_template('contracts.html')

@main_bp.route('/clauses')
@login_required
def clauses():
    """Clauses page"""
    return render_template('clauses.html')

@main_bp.route('/alerts')
@login_required
def alerts():
    """Alerts page"""
    return render_template('alerts.html')

@main_bp.route('/reports')
@login_required
def reports():
    """Reports page"""
    return render_template('reports.html')

@main_bp.route('/login')
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('login.html')

@main_bp.route('/register')
def register():
    """Registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('register.html')