#!/usr/bin/env python3
"""
Email Guardian - Local Application Configuration
Professional template system with Bootstrap and custom CSS
"""

import os
import sys
import platform
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create base class for SQLAlchemy
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)

# Configure app for local development
app.secret_key = 'local-dev-key-change-in-production'
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/local_email_guardian.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Add proxy fix for proper URL generation
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize database with app
db.init_app(app)

# Ensure upload directories exist
os.makedirs('uploads', exist_ok=True)
os.makedirs('data', exist_ok=True)
os.makedirs('instance', exist_ok=True)

# Initialize the application context and create tables
with app.app_context():
    # Import local models to avoid circular imports
    import local_models_standalone
    
    # Create all tables
    db.create_all()
    print("Database tables created successfully!")
    print(f"Application running with professional template system")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version.split()[0]}")

# Import routes after app context is set up
# Note: For local use, we'll create simplified routes to avoid complex imports
from flask import render_template, request, redirect, url_for, flash
import uuid
import os

@app.route('/')
def index():
    """Main index page with upload functionality"""
    from local_models_standalone import ProcessingSession
    recent_sessions = ProcessingSession.query.order_by(ProcessingSession.upload_time.desc()).limit(10).all()
    return render_template('index.html', recent_sessions=recent_sessions)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload and create processing session"""
    from local_models_standalone import ProcessingSession
    
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))

    if not file.filename.lower().endswith('.csv'):
        flash('Please upload a CSV file', 'error')
        return redirect(url_for('index'))

    try:
        # Save the uploaded file
        session_id = str(uuid.uuid4())
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_{filename}")
        file.save(filepath)
        
        # Create processing session
        session = ProcessingSession(
            id=session_id,
            filename=filename,
            status='uploaded'
        )
        db.session.add(session)
        db.session.commit()
        
        flash(f'File uploaded successfully! Session ID: {session_id}', 'success')
        return redirect(url_for('view_session', session_id=session_id))
        
    except Exception as e:
        flash(f'Upload failed: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/session/<session_id>')
def view_session(session_id):
    """View session details"""
    from local_models_standalone import ProcessingSession
    
    session = ProcessingSession.query.get_or_404(session_id)
    return render_template('processing.html', session=session)

if __name__ == '__main__':
    print("Starting Email Guardian with professional UI...")
    app.run(debug=True, host='127.0.0.1', port=5000)