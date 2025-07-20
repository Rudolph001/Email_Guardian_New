# Email Guardian - Local Setup Script
import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("ERROR: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✓ Python version: {sys.version.split()[0]}")
    return True

def install_requirements():
    """Install required packages"""
    print("\nInstalling requirements...")
    print("This may take a few minutes...")
    
    try:
        # First upgrade pip to latest version
        print("Upgrading pip...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ])
        
        # Install packages one by one for better error reporting
        packages = [
            "Flask>=2.3.0",
            "Flask-SQLAlchemy>=3.0.0", 
            "SQLAlchemy>=1.4.0",
            "Werkzeug>=2.3.0",
            "pandas>=1.5.0",
            "numpy>=1.21.0", 
            "scikit-learn>=1.2.0",
            "networkx>=2.8.0",
            "email-validator>=1.3.0",
            "waitress>=2.1.0",
            "python-dotenv>=0.19.0"
        ]
        
        for package in packages:
            print(f"Installing {package}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package
            ])
            
        print("✓ All requirements installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install package: {e}")
        print("\nTrying alternative installation method...")
        
        # Try installing from requirements file as fallback
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "local_requirements.txt"
            ])
            print("✓ Requirements installed successfully using fallback method")
            return True
        except subprocess.CalledProcessError as e2:
            print(f"ERROR: Both installation methods failed")
            print(f"Please manually install packages: pip install -r local_requirements.txt")
            return False

def create_directories():
    """Create necessary directories"""
    print("\nCreating directories...")
    directories = ['uploads', 'data', 'instance', 'static', 'templates']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")

def setup_database():
    """Initialize SQLite database"""
    print("\nSetting up database...")
    try:
        # Create instance directory
        os.makedirs('instance', exist_ok=True)
        
        # Create database file
        db_path = 'local_email_guardian.db'
        if not os.path.exists(db_path):
            # Create empty database file
            open(db_path, 'a').close()
            print(f"✓ Created database: {db_path}")
        else:
            print(f"✓ Database already exists: {db_path}")
        
        return True
    except Exception as e:
        print(f"ERROR: Failed to setup database: {e}")
        return False

def create_environment_file():
    """Create .env file for local development"""
    print("\nCreating environment configuration...")
    
    env_content = """# Email Guardian - Local Environment Configuration

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration (SQLite for local development)
DATABASE_URL=sqlite:///local_email_guardian.db

# Session Secret (generated randomly - change for production)
SESSION_SECRET=your-secret-key-here-change-in-production

# Application Settings
MAX_CONTENT_LENGTH=104857600
UPLOAD_FOLDER=uploads
DATA_FOLDER=data
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✓ Created .env file")
    else:
        print("✓ .env file already exists")

def display_instructions():
    """Display setup completion instructions"""
    print("\n" + "="*60)
    print("🎉 EMAIL GUARDIAN - LOCAL SETUP COMPLETE!")
    print("="*60)
    print("\nTo run the application locally:")
    print("\n1. Activate your virtual environment (recommended):")
    print("   python -m venv email_guardian_env")
    print("   # On Windows:")
    print("   email_guardian_env\\Scripts\\activate")
    print("   # On macOS/Linux:")
    print("   source email_guardian_env/bin/activate")
    
    print("\n2. Run the application:")
    print("   python local_app.py")
    
    print("\n3. Open your browser and go to:")
    print("   http://127.0.0.1:5000")
    
    print("\n4. For production deployment with Gunicorn:")
    print("   gunicorn --bind 127.0.0.1:5000 local_app:app")
    
    print("\nProject Structure:")
    print("├── local_app.py          # Main application entry point")
    print("├── local_config.py       # Local configuration")
    print("├── local_requirements.txt # Python dependencies")
    print("├── models.py             # Database models")
    print("├── routes.py             # Application routes")
    print("├── uploads/              # CSV file uploads")
    print("├── data/                 # Session data storage")
    print("├── static/               # CSS, JS, images")
    print("├── templates/            # HTML templates")
    print("└── local_email_guardian.db # SQLite database")
    
    print("\nTroubleshooting:")
    print("- If you encounter import errors, ensure all files are in the same directory")
    print("- For database issues, delete 'local_email_guardian.db' and restart")
    print("- Check the console output for any error messages")
    print("- Ensure port 5000 is not already in use")

def main():
    """Main setup function"""
    print("Email Guardian - Local Setup")
    print("="*40)
    
    if not check_python_version():
        return False
    
    if not install_requirements():
        return False
    
    create_directories()
    
    if not setup_database():
        return False
    
    create_environment_file()
    
    display_instructions()
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)