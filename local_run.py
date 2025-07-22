
#!/usr/bin/env python3
"""
Local development runner for Email Guardian
Alternative entry point with development-friendly settings
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def load_env_file():
    """Load environment variables from .env file if it exists"""
    env_file = Path(".env")
    if env_file.exists():
        print("Loading environment variables from .env file...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

def setup_development_environment():
    """Set up development environment variables"""
    
    # Load .env file if it exists
    load_env_file()
    
    # Set default development environment variables
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('FLASK_DEBUG', 'true')
    os.environ.setdefault('SESSION_SECRET', 'IbV9R1thLbcFKB9-UR4sHOe1ePE-zUamWbypp3ava7o')
    os.environ.setdefault('FAST_MODE', 'true')
    
    # Set database URL for local development (SQLite)
    if not os.environ.get('DATABASE_URL'):
        # Use simple local database file
        os.environ['DATABASE_URL'] = 'sqlite:///email_guardian_local.db'
        print(f"Using local SQLite database: email_guardian_local.db")
    
    # Ensure directories exist
    directories = ['uploads', 'data', 'instance']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"Created directory: {directory}")
    
    print(f"Database URL: {os.environ.get('DATABASE_URL')}")
    print(f"Session Secret: {'***set***' if os.environ.get('SESSION_SECRET') else 'NOT SET'}")
    
    # Mac-specific environment setup
    if sys.platform == 'darwin':  # macOS
        print("🍎 Detected macOS - applying Mac-specific configurations")
        # Set Mac-friendly locale environment
        os.environ.setdefault('LC_ALL', 'en_US.UTF-8')
        os.environ.setdefault('LANG', 'en_US.UTF-8')
        # Force UTF-8 mode for better file handling
        os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
        print("✓ Applied Mac UTF-8 configuration")

def main():
    """Main development runner"""
    print("=== Email Guardian Development Server ===")
    
    # Setup environment
    setup_development_environment()
    
    # Import and run the app
    try:
        from app import app
        print("Starting development server...")
        print("Access the application at: http://localhost:5000")
        print("Press Ctrl+C to stop the server")
        print()
        
        # Run the Flask development server
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=True
        )
        
    except ImportError as e:
        print(f"✗ Failed to import application: {e}")
        print("Make sure you've run the setup script: python local_setup.py")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
