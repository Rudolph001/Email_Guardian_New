#!/usr/bin/env python3
"""
Test local CSV upload functionality for Mac
This simulates the upload process to identify any remaining issues
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, '.')

def test_upload_process():
    """Test the complete upload process"""
    print("=== Testing Local Upload Process ===")
    
    try:
        # Import Flask app components
        from app import app, db
        from models import ProcessingSession, EmailRecord
        from data_processor import DataProcessor
        import uuid
        
        # Find a test CSV file
        upload_dir = Path('uploads')
        csv_files = list(upload_dir.glob('*.csv'))
        
        if not csv_files:
            print("❌ No CSV files found in uploads directory")
            return False
        
        test_file = csv_files[0]
        print(f"Testing with file: {test_file}")
        
        with app.app_context():
            # Create a test session
            session_id = str(uuid.uuid4())
            print(f"Created test session: {session_id}")
            
            # Create session record
            session = ProcessingSession()
            session.id = session_id
            session.filename = test_file.name
            session.status = 'uploaded'
            db.session.add(session)
            db.session.commit()
            print("✓ Session record created in database")
            
            # Test data processor
            data_processor = DataProcessor()
            
            try:
                print("Starting CSV processing test...")
                data_processor.process_csv(session_id, str(test_file))
                print("✓ CSV processing completed successfully")
                
                # Check results
                session = ProcessingSession.query.get(session_id)
                if session:
                    print(f"Session status: {session.status}")
                    print(f"Total records: {session.total_records}")
                    print(f"Processed records: {session.processed_records}")
                    
                    if session.error_message:
                        print(f"Error message: {session.error_message}")
                
                # Check email records
                email_count = EmailRecord.query.filter_by(session_id=session_id).count()
                print(f"Email records created: {email_count}")
                
                return True
                
            except Exception as processing_error:
                print(f"❌ Processing error: {str(processing_error)}")
                import traceback
                traceback.print_exc()
                return False
                
    except Exception as e:
        print(f"❌ Test setup error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_app_configuration():
    """Check app configuration"""
    print("\n=== Checking App Configuration ===")
    
    try:
        from app import app
        
        with app.app_context():
            print(f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
            print(f"Upload folder: {app.config.get('UPLOAD_FOLDER', 'uploads')}")
            print(f"Secret key: {'Set' if app.secret_key else 'Not set'}")
            
            # Test database connection
            from models import ProcessingSession
            session_count = ProcessingSession.query.count()
            print(f"Total sessions in database: {session_count}")
            
            return True
            
    except Exception as e:
        print(f"❌ Configuration check failed: {str(e)}")
        return False

def test_web_access():
    """Test web interface access"""
    print("\n=== Testing Web Interface ===")
    
    try:
        from app import app
        
        with app.test_client() as client:
            # Test index page
            response = client.get('/')
            print(f"Index page status: {response.status_code}")
            
            if response.status_code == 200:
                print("✓ Web interface is accessible")
                return True
            else:
                print(f"❌ Web interface returned status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Web interface test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("=== Email Guardian Local Upload Test ===")
    
    # Set Mac environment
    if sys.platform == 'darwin':
        os.environ.setdefault('LC_ALL', 'en_US.UTF-8')
        os.environ.setdefault('LANG', 'en_US.UTF-8')
        os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
        print("✓ Applied Mac environment settings")
    
    success_count = 0
    total_tests = 3
    
    if check_app_configuration():
        success_count += 1
    
    if test_web_access():
        success_count += 1
    
    if test_upload_process():
        success_count += 1
    
    print(f"\n=== Test Results: {success_count}/{total_tests} passed ===")
    
    if success_count == total_tests:
        print("🎉 All tests passed! Upload functionality should work correctly.")
        print("\nNext steps:")
        print("1. Start the app: python3 local_run.py")
        print("2. Open http://localhost:5000 in your browser")
        print("3. Try uploading a CSV file")
    else:
        print("⚠️ Some tests failed. Check the error messages above.")
        print("The CSV upload may not work correctly until these issues are resolved.")

if __name__ == "__main__":
    main()