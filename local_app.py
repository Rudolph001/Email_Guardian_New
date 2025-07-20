# Email Guardian - Local Application Entry Point
import os
import logging
import platform
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from local_config import LocalConfig

# Set up logging for development
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the Flask app
app = Flask(__name__)
app.config.from_object(LocalConfig)

# Initialize extensions
db.init_app(app)

# Create upload and data directories
os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)
os.makedirs(app.config.get('DATA_FOLDER', 'data'), exist_ok=True)

# Import models and routes after app creation
with app.app_context():
    # Import models to ensure tables are created
    import models
    
    # Create database tables
    db.create_all()

# Import routes - this must be done after app is created
import routes

if __name__ == '__main__':
    # Check if running on Windows and use appropriate server
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