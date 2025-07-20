#!/usr/bin/env python3
"""
Email Guardian - Simple Local Launcher
Fixed version for Windows with better error handling
"""

import os
import sys

def check_dependencies():
    """Check if required packages are installed"""
    required = ['flask', 'flask_sqlalchemy']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("Missing dependencies:")
        for pkg in missing:
            print(f"  - {pkg}")
        print("\nPlease install with:")
        print("pip install flask flask-sqlalchemy")
        return False
    return True

def main():
    print("Email Guardian - Local Setup")
    print("=" * 40)
    
    if not check_dependencies():
        return
    
    # Set up directories
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    print("Dependencies OK")
    print("Directories created")
    print("Starting application...")
    print()
    
    # Import and run the app
    try:
        from local_standalone import app
        print("Email Guardian is ready!")
        print("Open your browser to: http://127.0.0.1:5000")
        print("Press Ctrl+C to stop")
        print()
        app.run(debug=True, host='127.0.0.1', port=5000)
    except Exception as e:
        print(f"Error starting application: {e}")
        print("Make sure Flask is installed: pip install flask flask-sqlalchemy")

if __name__ == '__main__':
    main()