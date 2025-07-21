
#!/usr/bin/env python3
"""
Local setup script for Email Guardian
Run this script to set up the application for local development
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def install_dependencies():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        sys.exit(1)

def create_directories():
    """Create necessary directories"""
    print("Creating necessary directories...")
    directories = ['uploads', 'data', 'instance', 'static/css', 'static/js', 'templates']
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✓ Directories created")

def setup_database():
    """Initialize SQLite database"""
    print("Setting up SQLite database...")
    db_path = "instance/email_guardian.db"
    
    # Create empty database file if it doesn't exist
    if not os.path.exists(db_path):
        Path(db_path).touch()
    
    print("✓ Database setup complete")

def create_env_file():
    """Create a sample .env file"""
    print("Creating sample environment file...")
    
    env_content = """# Email Guardian Local Configuration
# Copy this to .env and modify as needed

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=true
SESSION_SECRET=your-secret-key-change-this-in-production

# Database Configuration (optional - defaults to SQLite)
# DATABASE_URL=sqlite:///email_guardian.db

# Performance Configuration
FAST_MODE=true
CHUNK_SIZE=1000
MAX_ML_RECORDS=5000
"""
    
    with open(".env.example", "w") as f:
        f.write(env_content)
    
    print("✓ Sample environment file created (.env.example)")
    print("  Copy .env.example to .env and modify as needed")

def main():
    """Main setup function"""
    print("=== Email Guardian Local Setup ===")
    print()
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("✗ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Run setup steps
    install_dependencies()
    create_directories()
    setup_database()
    create_env_file()
    
    print()
    print("=== Setup Complete! ===")
    print()
    print("To run the application:")
    print("1. Copy .env.example to .env and modify as needed")
    print("2. Run: python main.py")
    print("3. Open your browser to http://localhost:5000")
    print()
    print("For production deployment, use:")
    print("gunicorn --bind 0.0.0.0:5000 main:app")

if __name__ == "__main__":
    main()
