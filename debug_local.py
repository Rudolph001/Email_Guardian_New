#!/usr/bin/env python3
"""
Debug script for local Email Guardian issues
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def check_environment():
    """Check local environment setup"""
    print("=== Email Guardian Local Environment Debug ===\n")
    
    # Check directories
    directories = ['uploads', 'data', 'instance']
    print("Directory Check:")
    for directory in directories:
        path = Path(directory)
        if path.exists():
            print(f"✓ {directory}/ exists")
        else:
            print(f"✗ {directory}/ missing - creating...")
            path.mkdir(exist_ok=True)
            print(f"✓ {directory}/ created")
    print()
    
    # Check database
    db_path = Path('instance/email_guardian.db')
    print("Database Check:")
    print(f"Database path: {db_path.absolute()}")
    if db_path.exists():
        print(f"✓ Database exists (size: {db_path.stat().st_size} bytes)")
    else:
        print("✗ Database doesn't exist - will be created on first run")
    print()
    
    # Set environment variables
    os.environ['DATABASE_URL'] = f'sqlite:///{db_path.absolute()}'
    os.environ['SESSION_SECRET'] = 'IbV9R1thLbcFKB9-UR4sHOe1ePE-zUamWbypp3ava7o'
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = 'true'
    
    print("Environment Variables:")
    print(f"DATABASE_URL: {os.environ.get('DATABASE_URL')}")
    print(f"SESSION_SECRET: {'***set***' if os.environ.get('SESSION_SECRET') else 'NOT SET'}")
    print(f"FLASK_ENV: {os.environ.get('FLASK_ENV')}")
    print()

def test_database_connection():
    """Test database connection"""
    print("Testing Database Connection:")
    try:
        from app import app, db
        with app.app_context():
            # Try to create tables
            db.create_all()
            print("✓ Database connection successful")
            print("✓ Tables created/verified")
            
            # Test basic query
            from models import ProcessingSession
            count = ProcessingSession.query.count()
            print(f"✓ Database query successful - {count} sessions found")
            
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False
    return True

def test_file_upload_permissions():
    """Test file upload directory permissions"""
    print("Testing File Upload Permissions:")
    try:
        test_file = Path('uploads/test.txt')
        test_file.write_text('test')
        if test_file.exists():
            print("✓ Can write to uploads directory")
            test_file.unlink()  # Delete test file
            print("✓ Can delete from uploads directory")
        else:
            print("✗ Cannot write to uploads directory")
    except Exception as e:
        print(f"✗ Upload permission error: {e}")

def main():
    """Main debug function"""
    check_environment()
    
    if test_database_connection():
        test_file_upload_permissions()
        print("\n=== Debug Complete ===")
        print("Environment appears to be set up correctly.")
        print("Try running: python local_run.py")
    else:
        print("\n=== Debug Failed ===")
        print("Database connection failed. Check the error messages above.")

if __name__ == "__main__":
    main()