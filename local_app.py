# Email Guardian - Local Application Entry Point
import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from local_config import LocalConfig

# Set up logging for development
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def create_app(config_class=LocalConfig):
    """Application factory for local development"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    
    # Create upload and data directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)
    
    # Import routes after app creation to avoid circular imports
    with app.app_context():
        # Import models to ensure tables are created
        import models
        
        # Create database tables
        db.create_all()
        
        # Import and register routes
        from routes import *
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    # Check if running on Windows and use appropriate server
    import platform
    
    if platform.system() == 'Windows':
        try:
            from waitress import serve
            print("Starting Email Guardian on Windows with Waitress server...")
            print("Open your browser to: http://127.0.0.1:5000")
            print("Press Ctrl+C to stop the server")
            serve(app, host='127.0.0.1', port=5000)
        except ImportError:
            print("Waitress not available, using Flask development server...")
            app.run(
                host='127.0.0.1',
                port=5000,
                debug=True,
                threaded=True
            )
    else:
        # Unix/Linux/macOS - use Flask development server
        print("Starting Email Guardian...")
        print("Open your browser to: http://127.0.0.1:5000")
        print("Press Ctrl+C to stop the server")
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=True,
            threaded=True
        )