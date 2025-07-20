# Email Guardian - Local Configuration
import os
import secrets

class LocalConfig:
    """Local development configuration"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SESSION_SECRET') or secrets.token_hex(32)
    DEBUG = True
    
    # Database Configuration - SQLite for local development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///local_email_guardian.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size
    UPLOAD_FOLDER = 'uploads'
    DATA_FOLDER = 'data'
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
    
    # Application Configuration
    ITEMS_PER_PAGE = 50
    MAX_RECORDS_PER_SESSION = 100000
    
    # Development Settings
    TESTING = False
    WTF_CSRF_ENABLED = True

# For PostgreSQL (uncomment and configure if needed)
class PostgreSQLConfig(LocalConfig):
    """PostgreSQL configuration for local development"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://username:password@localhost/email_guardian_local'