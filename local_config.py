#!/usr/bin/env python3
"""
Local development configuration for Email Guardian
Optimized for local development with proper error handling
"""

import os
import logging

def setup_local_environment():
    """Configure environment for local development"""
    
    # Basic Flask settings
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('FLASK_DEBUG', 'true')
    
    # Session secret key - use a consistent key for local development
    os.environ.setdefault('SESSION_SECRET', 'local-dev-secret-key-email-guardian-2025')
    
    # Database configuration for local development
    if not os.environ.get('DATABASE_URL'):
        # Ensure instance directory exists
        os.makedirs('instance', exist_ok=True)
        # Use absolute path for SQLite database
        db_path = os.path.abspath('instance/email_guardian.db')
        os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
        print(f"Local SQLite database: {db_path}")
    
    # Performance settings for local development
    os.environ.setdefault('FAST_MODE', 'true')
    
    # Logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=== Email Guardian Local Development ===")
    print(f"Database: {os.environ.get('DATABASE_URL')}")
    print(f"Session Secret: {'***configured***' if os.environ.get('SESSION_SECRET') else 'NOT SET'}")
    print(f"Fast Mode: {os.environ.get('FAST_MODE')}")
    print("=========================================")

if __name__ == "__main__":
    setup_local_environment()