#!/usr/bin/env python3
"""
Database migration script for local SQLite database
Run this to update your local database schema to match the current models
"""

import os
import sqlite3
import sys
from pathlib import Path

def setup_environment():
    """Set up environment for local development"""
    os.environ.setdefault('SESSION_SECRET', 'dev-secret-change-in-production')
    os.environ.setdefault('FAST_MODE', 'true')
    
    # Set database URL for local development (SQLite)
    db_path = Path('instance/email_guardian.db').absolute()
    os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
    
    # Ensure directories exist
    Path('instance').mkdir(exist_ok=True)

def migrate_database():
    """Migrate the local SQLite database"""
    db_path = 'instance/email_guardian.db'
    
    print("Migrating local SQLite database...")
    
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if description column exists in attachment_keywords table
        cursor.execute("PRAGMA table_info(attachment_keywords)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'description' not in columns:
            print("Adding description column to attachment_keywords table...")
            cursor.execute("ALTER TABLE attachment_keywords ADD COLUMN description TEXT")
            conn.commit()
            print("✓ Added description column")
        else:
            print("✓ Description column already exists")
            
        # Check if attachment_keywords table exists, if not create it
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='attachment_keywords'")
        if not cursor.fetchone():
            print("Creating attachment_keywords table...")
            cursor.execute("""
                CREATE TABLE attachment_keywords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    keyword VARCHAR(100) NOT NULL,
                    category VARCHAR(50),
                    risk_score FLOAT DEFAULT 0.5,
                    description TEXT,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            conn.commit()
            print("✓ Created attachment_keywords table")
            
        # Create other tables if they don't exist (basic structure)
        tables_to_check = [
            ('processing_session', """
                CREATE TABLE processing_session (
                    id VARCHAR(36) PRIMARY KEY,
                    filename VARCHAR(255),
                    upload_time DATETIME,
                    status VARCHAR(50) DEFAULT 'Active',
                    total_records INTEGER DEFAULT 0,
                    processed_records INTEGER DEFAULT 0,
                    analysis_complete BOOLEAN DEFAULT 0
                )
            """),
            ('email_record', """
                CREATE TABLE email_record (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id VARCHAR(36),
                    record_id VARCHAR(100),
                    sender VARCHAR(255),
                    recipients TEXT,
                    recipients_email_domain VARCHAR(255),
                    subject TEXT,
                    time DATETIME,
                    attachments TEXT,
                    justification TEXT,
                    ml_risk_score FLOAT,
                    excluded_by_rule VARCHAR(255),
                    whitelisted BOOLEAN DEFAULT 0,
                    case_status VARCHAR(50) DEFAULT 'Active',
                    FOREIGN KEY (session_id) REFERENCES processing_session (id)
                )
            """),
            ('whitelist_domain', """
                CREATE TABLE whitelist_domain (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain VARCHAR(255) UNIQUE NOT NULL,
                    added_date DATETIME,
                    is_active BOOLEAN DEFAULT 1,
                    notes TEXT
                )
            """),
            ('rule', """
                CREATE TABLE rule (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(255) NOT NULL,
                    conditions TEXT NOT NULL,
                    priority VARCHAR(20) DEFAULT 'Medium',
                    is_active BOOLEAN DEFAULT 1,
                    created_date DATETIME,
                    description TEXT
                )
            """)
        ]
        
        for table_name, create_sql in tables_to_check:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if not cursor.fetchone():
                print(f"Creating {table_name} table...")
                cursor.execute(create_sql)
                conn.commit()
                print(f"✓ Created {table_name} table")
        
        print("✓ Database migration completed successfully")
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
    
    return True

def initialize_with_flask():
    """Initialize database using Flask-SQLAlchemy (recommended approach)"""
    try:
        setup_environment()
        
        # Import Flask app and models
        from app import app, db
        import models
        
        with app.app_context():
            print("Creating all tables using Flask-SQLAlchemy...")
            db.create_all()
            print("✓ All tables created successfully")
            
        return True
    except Exception as e:
        print(f"✗ Flask initialization failed: {e}")
        return False

def main():
    """Main migration function"""
    print("=== Email Guardian Local Database Migration ===")
    print()
    
    # Try Flask-SQLAlchemy approach first (recommended)
    if initialize_with_flask():
        print("Database is ready for local development!")
        return
    
    # Fallback to direct SQLite migration
    print("Falling back to direct SQLite migration...")
    if migrate_database():
        print("Database migration completed!")
        print("You can now run: python3 local_run.py")
    else:
        print("Migration failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()