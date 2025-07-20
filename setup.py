#!/usr/bin/env python3
"""
Email Guardian - Local Installation Setup
Simple one-file installer for Windows/Mac/Linux
"""

import os
import sys
import subprocess
import platform

def check_python():
    """Check Python version compatibility"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported")
        print("Please install Python 3.8 or higher")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_packages():
    """Install required packages"""
    print("\nInstalling packages...")
    
    packages = [
        "Flask>=3.0.0",
        "Flask-SQLAlchemy>=3.1.0", 
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scikit-learn>=1.3.0",
        "networkx>=3.0.0",
        "email-validator>=2.0.0",
        "waitress>=2.1.0"
    ]
    
    for package in packages:
        try:
            print(f"Installing {package.split('>=')[0]}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package, "--user", "--quiet"
            ])
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    
    print("✅ All packages installed")
    return True

def create_directories():
    """Create necessary directories"""
    dirs = ['uploads', 'data', 'static', 'templates']
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)
    print("✅ Directories created")

def main():
    """Main setup function"""
    print("Email Guardian - Local Setup")
    print("=" * 40)
    
    if not check_python():
        return False
    
    if not install_packages():
        print("\n❌ Installation failed")
        print("Try running: pip install -r requirements_local.txt")
        return False
    
    create_directories()
    
    print("\n✅ Setup complete!")
    print("\nTo start Email Guardian:")
    print("  python local_standalone.py")
    print("\nThen open: http://127.0.0.1:5000")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)