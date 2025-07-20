#!/usr/bin/env python3
"""
Email Guardian - Local Application with Professional UI
Standalone version that avoids circular imports
"""

import os
import sys
import platform
import logging
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

print("Starting Email Guardian with professional template system...")
print("This version uses the same beautiful interface as the Replit deployment.")
print()

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

# Define models inline to avoid import issues
from sqlalchemy import Text, JSON

class ProcessingSession(db.Model):
    __tablename__ = 'processing_sessions'
    
    id = db.Column(db.String(36), primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    total_records = db.Column(db.Integer, default=0)
    processed_records = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='uploaded')
    error_message = db.Column(Text)
    processing_stats = db.Column(JSON)
    data_path = db.Column(db.String(500))
    is_compressed = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<ProcessingSession {self.id}>'

# Routes
@app.route('/')
def index():
    """Main index page with upload functionality"""
    recent_sessions = ProcessingSession.query.order_by(ProcessingSession.upload_time.desc()).limit(10).all()
    return render_template('index.html', recent_sessions=recent_sessions)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload and create processing session"""
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
    session = ProcessingSession.query.get_or_404(session_id)
    return render_template('processing.html', session=session)

@app.route('/sessions')
def list_sessions():
    """List all processing sessions"""
    sessions = ProcessingSession.query.order_by(ProcessingSession.upload_time.desc()).all()
    return render_template('dashboard.html', sessions=sessions)

# Initialize the database
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")
    print(f"Application running with professional template system")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version.split()[0]}")

if __name__ == '__main__':
    print()
    print("Email Guardian is ready!")
    print("Access at: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server")
    print()
    app.run(debug=True, host='127.0.0.1', port=5000)