#!/usr/bin/env python3
"""
One-click fix for Mac CSV upload issues
Run this to apply all Mac-specific fixes at once
"""

import os
import sys
import subprocess
from pathlib import Path

def apply_mac_environment():
    """Apply Mac-specific environment variables"""
    print("Applying Mac-specific environment settings...")
    
    # Set environment variables
    env_vars = {
        'LC_ALL': 'en_US.UTF-8',
        'LANG': 'en_US.UTF-8',
        'PYTHONIOENCODING': 'utf-8',
        'PYTHONLEGACYWINDOWSSTDIO': 'utf-8'
    }
    
    for var, value in env_vars.items():
        os.environ[var] = value
        print(f"Set {var}={value}")

def fix_file_permissions():
    """Fix file permissions for Mac"""
    print("Fixing file permissions...")
    
    # Ensure upload directory exists and has correct permissions
    upload_dir = Path('uploads')
    upload_dir.mkdir(exist_ok=True)
    
    try:
        # Set proper permissions (readable/writable by owner, readable by group)
        upload_dir.chmod(0o755)
        print(f"Set permissions for uploads directory: {upload_dir}")
        
        # Fix permissions for existing files
        for file_path in upload_dir.glob('*'):
            if file_path.is_file():
                file_path.chmod(0o644)
                print(f"Fixed permissions for: {file_path.name}")
                
    except Exception as e:
        print(f"Warning: Could not fix permissions: {e}")

def install_mac_dependencies():
    """Install any Mac-specific dependencies"""
    print("Checking Mac dependencies...")
    
    try:
        import chardet
        print("✓ chardet is installed")
    except ImportError:
        print("Installing chardet for encoding detection...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'chardet'], check=True)

def create_mac_startup_script():
    """Create a Mac-optimized startup script"""
    script_content = '''#!/bin/bash
# Mac-optimized Email Guardian startup script

echo "🍎 Starting Email Guardian with Mac optimizations..."

# Set Mac-friendly environment variables
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
export PYTHONIOENCODING=utf-8

# Create necessary directories
mkdir -p uploads data instance

# Set file permissions
chmod 755 uploads data instance
find uploads -type f -exec chmod 644 {} \\; 2>/dev/null || true

# Start the application
echo "Starting Email Guardian..."
python3 local_run.py
'''
    
    script_path = Path('start_mac.sh')
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    script_path.chmod(0o755)
    print(f"Created Mac startup script: {script_path}")

def test_csv_functionality():
    """Test CSV functionality with a simple test"""
    print("Testing CSV functionality...")
    
    try:
        import pandas as pd
        import chardet
        
        # Create a simple test CSV
        test_csv = Path('test_mac.csv')
        test_data = '''time,sender,subject,recipients
2025-01-01,test@example.com,Test Subject,recipient@example.com
2025-01-02,test2@example.com,Another Test,recipient2@example.com'''
        
        with open(test_csv, 'w', encoding='utf-8') as f:
            f.write(test_data)
        
        # Test reading the CSV
        df = pd.read_csv(test_csv)
        print(f"✓ CSV test successful: {len(df)} rows, {len(df.columns)} columns")
        
        # Test encoding detection
        with open(test_csv, 'rb') as f:
            raw_data = f.read()
        result = chardet.detect(raw_data)
        print(f"✓ Encoding detection: {result['encoding']} (confidence: {result['confidence']:.2f})")
        
        # Clean up
        test_csv.unlink()
        return True
        
    except Exception as e:
        print(f"❌ CSV test failed: {e}")
        return False

def main():
    """Apply all Mac fixes"""
    print("=== Email Guardian Mac Fix Tool ===")
    print(f"Platform: {sys.platform}")
    
    if sys.platform != 'darwin':
        print("ℹ️ This tool is designed for macOS, but some fixes may still be helpful.")
    
    # Apply all fixes
    try:
        apply_mac_environment()
        fix_file_permissions()
        install_mac_dependencies()
        create_mac_startup_script()
        
        if test_csv_functionality():
            print("\n🎉 All Mac fixes applied successfully!")
            print("\nNext steps:")
            print("1. Use the new startup script: ./start_mac.sh")
            print("2. Or run with environment: python3 local_run.py")
            print("3. Try uploading a CSV file exported as 'CSV UTF-8' from Excel")
            print("4. If issues persist, run: python3 debug_mac_upload.py")
        else:
            print("\n⚠️ Some issues detected. Please check the error messages above.")
            
    except Exception as e:
        print(f"\n❌ Error applying fixes: {e}")
        print("Please run the individual components manually or contact support.")

if __name__ == "__main__":
    main()