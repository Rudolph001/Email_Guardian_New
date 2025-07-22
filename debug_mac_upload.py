#!/usr/bin/env python3
"""
Mac-specific CSV upload debugging for Email Guardian
Run this AFTER attempting an upload to see what went wrong
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging to see all debug info
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def check_upload_directory():
    """Check upload directory and recent files"""
    print("=== Upload Directory Check ===")
    
    upload_dirs = ['uploads', './uploads']
    for upload_dir in upload_dirs:
        if os.path.exists(upload_dir):
            print(f"✓ Found upload directory: {upload_dir}")
            files = os.listdir(upload_dir)
            if files:
                print(f"Files in upload directory: {len(files)}")
                # Show recent files
                files_with_time = [(f, os.path.getmtime(os.path.join(upload_dir, f))) for f in files]
                files_with_time.sort(key=lambda x: x[1], reverse=True)
                print("Recent uploads:")
                for f, mtime in files_with_time[:5]:
                    size = os.path.getsize(os.path.join(upload_dir, f))
                    print(f"  {f} ({size} bytes)")
                return upload_dir, files
            else:
                print(f"Upload directory {upload_dir} is empty")
        else:
            print(f"❌ Upload directory {upload_dir} does not exist")
    
    return None, []

def check_database():
    """Check database and recent sessions"""
    print("\n=== Database Check ===")
    
    try:
        # Add current directory to Python path
        sys.path.insert(0, '.')
        
        # Import and initialize the app
        from app import app, db
        from models import ProcessingSession
        
        with app.app_context():
            # Check recent sessions
            recent_sessions = ProcessingSession.query.order_by(ProcessingSession.upload_time.desc()).limit(5).all()
            
            if recent_sessions:
                print(f"✓ Found {len(recent_sessions)} recent sessions:")
                for session in recent_sessions:
                    print(f"  {session.id}: {session.filename} - {session.status}")
                    if session.error_message:
                        print(f"    Error: {session.error_message}")
                return recent_sessions
            else:
                print("❌ No sessions found in database")
                return []
    
    except Exception as e:
        print(f"❌ Database check failed: {str(e)}")
        return []

def check_mac_environment():
    """Check Mac-specific environment"""
    print("\n=== Mac Environment Check ===")
    
    print(f"Platform: {sys.platform}")
    if sys.platform == 'darwin':
        print("✓ Running on macOS")
        
        # Check locale settings
        print(f"LC_ALL: {os.environ.get('LC_ALL', 'Not set')}")
        print(f"LANG: {os.environ.get('LANG', 'Not set')}")
        print(f"PYTHONIOENCODING: {os.environ.get('PYTHONIOENCODING', 'Not set')}")
        
        # Check Python encoding
        import locale
        try:
            print(f"Default locale: {locale.getdefaultlocale()}")
            print(f"Preferred encoding: {locale.getpreferredencoding()}")
        except:
            pass
    else:
        print("ℹ️ Not running on macOS")

def test_csv_file(csv_path):
    """Test a specific CSV file"""
    print(f"\n=== Testing CSV File: {csv_path} ===")
    
    if not os.path.exists(csv_path):
        print(f"❌ File not found: {csv_path}")
        return False
    
    try:
        import pandas as pd
        import chardet
        
        # Check file size
        size = os.path.getsize(csv_path)
        print(f"File size: {size} bytes")
        
        # Detect encoding
        with open(csv_path, 'rb') as f:
            raw_data = f.read(10000)
        
        result = chardet.detect(raw_data)
        encoding = result.get('encoding', 'unknown')
        confidence = result.get('confidence', 0)
        print(f"Detected encoding: {encoding} (confidence: {confidence:.2f})")
        
        # Try to read with detected encoding
        df = pd.read_csv(csv_path, nrows=5, encoding=encoding)
        print(f"✓ Successfully read CSV: {len(df.columns)} columns, {len(df)} rows")
        print(f"Columns: {list(df.columns)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading CSV: {str(e)}")
        return False

def main():
    """Main debugging function"""
    print("=== Email Guardian Mac Upload Debugger ===")
    
    # Check Mac environment
    check_mac_environment()
    
    # Check upload directory
    upload_dir, files = check_upload_directory()
    
    # Check database
    sessions = check_database()
    
    # If we have recent uploads, test them
    if upload_dir and files:
        latest_file = files[0] if files else None
        if latest_file:
            latest_path = os.path.join(upload_dir, latest_file)
            test_csv_file(latest_path)
    
    # Allow testing a specific file
    if len(sys.argv) > 1:
        test_csv_file(sys.argv[1])
    
    print("\n=== Debug Complete ===")
    
    # Provide specific recommendations
    print("\n=== Recommendations ===")
    if sys.platform == 'darwin':
        print("For Mac users:")
        print("1. Export CSV from Excel as 'CSV UTF-8 (Comma delimited)'")
        print("2. Ensure file permissions allow reading: chmod 644 your_file.csv")
        print("3. Try running: python local_run.py with these environment variables:")
        print("   export LC_ALL=en_US.UTF-8")
        print("   export LANG=en_US.UTF-8")
        print("   export PYTHONIOENCODING=utf-8")
    
    if not sessions:
        print("4. Database seems empty - the upload might not be reaching the database")
        print("5. Check Flask application logs for errors")
    
    if not files:
        print("6. No uploaded files found - the file upload itself might be failing")
        print("7. Check file permissions and available disk space")

if __name__ == "__main__":
    main()