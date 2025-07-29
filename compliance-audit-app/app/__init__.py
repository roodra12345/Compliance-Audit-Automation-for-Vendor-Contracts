import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from apscheduler.schedulers.background import BackgroundScheduler
from config.config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
jwt = JWTManager()
cors = CORS()
mail = Mail()
scheduler = BackgroundScheduler()

def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    mail.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from app.api import auth_bp, contracts_bp, clauses_bp, reports_bp, alerts_bp, chat_bp, code_gen_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(contracts_bp, url_prefix='/api/contracts')
    app.register_blueprint(clauses_bp, url_prefix='/api/clauses')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    app.register_blueprint(alerts_bp, url_prefix='/api/alerts')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(code_gen_bp, url_prefix='/api/code-gen')
    
    # Register main routes (for serving the UI)
    from app import routes
    app.register_blueprint(routes.main_bp)
    
    # Setup scheduler
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        from app.utils.scheduler_tasks import setup_scheduler
        setup_scheduler(app, scheduler)
        scheduler.start()
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default admin user if not exists
        from app.models import User
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@compliance-audit.com',
                role='admin'
            )
            admin.set_password('admin123')  # Change this in production!
            db.session.add(admin)
            db.session.commit()
    
    return app

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))