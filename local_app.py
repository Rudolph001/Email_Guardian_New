# Email Guardian - Local Application Entry Point
import os
import logging
import platform
from flask import Flask

# Set up logging for development
logging.basicConfig(level=logging.DEBUG)

# Create the Flask app first
app = Flask(__name__)

# Configure the app
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local_email_guardian.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DATA_FOLDER'] = 'data'

# Create upload and data directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)

# Now initialize SQLAlchemy with the configured app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Import models and create tables
with app.app_context():
    import models
    db.create_all()
    print("Database tables created successfully!")

# Import routes after everything is set up
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