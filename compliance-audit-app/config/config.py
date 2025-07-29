import os
import secrets
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '..', '.env'))

class Config:
    # Flask - Auto-generate secure keys if not provided
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '..', 'compliance_audit.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT - Auto-generate secure key if not provided
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or secrets.token_hex(32)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # OpenAI Configuration (standard OpenAI API)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Azure Services (optional - for OCR)
    AZURE_COMPUTER_VISION_ENDPOINT = os.environ.get('AZURE_COMPUTER_VISION_ENDPOINT')
    AZURE_COMPUTER_VISION_KEY = os.environ.get('AZURE_COMPUTER_VISION_KEY')
    
    # Legacy Azure OpenAI support (will use OpenAI API if not set)
    AZURE_OPENAI_ENDPOINT = os.environ.get('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_KEY = os.environ.get('AZURE_OPENAI_KEY')
    AZURE_OPENAI_DEPLOYMENT_NAME = os.environ.get('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4')
    
    # Email (optional)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', '')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587)) if os.environ.get('MAIL_PORT') else None
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # File Upload
    UPLOAD_FOLDER = os.path.join(basedir, '..', 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'pdf'}
    
    # Redis/Celery (optional)
    REDIS_URL = os.environ.get('REDIS_URL', '')
    CELERY_BROKER_URL = REDIS_URL if REDIS_URL else None
    CELERY_RESULT_BACKEND = REDIS_URL if REDIS_URL else None
    
    # Scheduler
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = 'UTC'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}