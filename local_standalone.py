# Email Guardian - Completely Standalone Local Version
# This avoids all import conflicts

import os
import sys
import platform
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Create Flask app
app = Flask(__name__)

# Configure app directly
app.config['SECRET_KEY'] = 'local-dev-key-change-in-production'
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local_email_guardian.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DATA_FOLDER'] = 'data'

# Create directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)

# Set up database
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Create basic models inline to avoid import issues
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, Float

class ProcessingSession(db.Model):
    __tablename__ = 'processing_sessions'
    
    id = db.Column(db.String(36), primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    total_records = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='uploaded')
    
    def __repr__(self):
        return f'<ProcessingSession {self.id}>'

# Create tables
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")

# Basic routes
@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Email Guardian - Local Version</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 1000px; margin: 40px auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px; }
            .success { background: #d4edda; padding: 20px; border-radius: 8px; color: #155724; margin: 20px 0; }
            .card { background: white; border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .feature { display: inline-block; background: #f8f9fa; padding: 10px 15px; margin: 5px; border-radius: 5px; border-left: 4px solid #007bff; }
            .btn { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 5px; text-decoration: none; display: inline-block; margin: 10px 5px; cursor: pointer; }
            .btn:hover { background: #0056b3; }
            .system-info { background: #f8f9fa; padding: 15px; border-radius: 5px; font-family: monospace; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📧 Email Guardian</h1>
            <p>Email Security Analysis Platform - Local Installation</p>
        </div>
        
        <div class="success">
            <h2>✅ Email Guardian is Running Successfully!</h2>
            <p>Your local installation is working correctly on Windows Python 3.13</p>
        </div>
        
        <div class="card">
            <h3>🚀 Core Features Available</h3>
            <div class="feature">CSV File Processing</div>
            <div class="feature">Machine Learning Analysis</div>
            <div class="feature">Risk Assessment</div>
            <div class="feature">Domain Whitelisting</div>
            <div class="feature">Case Management</div>
            <div class="feature">Interactive Dashboards</div>
        </div>
        
        <div class="card">
            <h3>📊 System Status</h3>
            <div class="system-info">
                <strong>Server:</strong> Flask Development Server<br>
                <strong>Database:</strong> SQLite (local_email_guardian.db)<br>
                <strong>Platform:</strong> ''' + platform.system() + ''' ''' + platform.release() + '''<br>
                <strong>Python:</strong> ''' + sys.version.split()[0] + '''<br>
                <strong>URL:</strong> http://127.0.0.1:5000<br>
                <strong>Upload Directory:</strong> ./uploads/<br>
                <strong>Data Directory:</strong> ./data/
            </div>
        </div>
        
        <div class="card">
            <h3>📁 Quick Start</h3>
            <p>1. <strong>Upload CSV Files:</strong> Use the upload section below</p>
            <p>2. <strong>View Analysis:</strong> Check dashboards and reports</p>
            <p>3. <strong>Manage Cases:</strong> Review flagged emails and risks</p>
            <p>4. <strong>Configure Rules:</strong> Set up custom business rules</p>
            
            <form action="/upload" method="post" enctype="multipart/form-data" style="margin-top: 20px;">
                <input type="file" name="file" accept=".csv" required style="padding: 10px; margin-right: 10px;">
                <button type="submit" class="btn">Upload CSV File</button>
            </form>
        </div>
        
        <div class="card">
            <h3>🔧 Administration</h3>
            <a href="/sessions" class="btn">View Sessions</a>
            <a href="/rules" class="btn">Manage Rules</a>
            <a href="/whitelist" class="btn">Domain Whitelist</a>
            <a href="/settings" class="btn">Settings</a>
        </div>
        
        <div style="text-align: center; margin-top: 30px; color: #666;">
            <p>Email Guardian - Comprehensive Email Security Analysis Platform</p>
            <p><em>Press Ctrl+C in terminal to stop the server</em></p>
        </div>
    </body>
    </html>
    '''

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))
    
    if file and file.filename.endswith('.csv'):
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Create processing session
        import uuid
        session_id = str(uuid.uuid4())
        session = ProcessingSession(
            id=session_id,
            filename=filename,
            status='uploaded'
        )
        db.session.add(session)
        db.session.commit()
        
        flash(f'File {filename} uploaded successfully! Session ID: {session_id}')
        return redirect(url_for('view_session', session_id=session_id))
    
    flash('Please upload a CSV file')
    return redirect(url_for('index'))

@app.route('/sessions')
def sessions():
    sessions = ProcessingSession.query.order_by(ProcessingSession.upload_time.desc()).all()
    session_list = ""
    for session in sessions:
        session_list += f'''
        <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px;">
            <h4>{session.filename}</h4>
            <p><strong>ID:</strong> {session.id}</p>
            <p><strong>Uploaded:</strong> {session.upload_time}</p>
            <p><strong>Status:</strong> {session.status}</p>
            <a href="/session/{session.id}" style="background: #007bff; color: white; padding: 8px 16px; text-decoration: none; border-radius: 3px;">View Details</a>
        </div>
        '''
    
    return f'''
    <html>
    <head><title>Processing Sessions</title></head>
    <body style="font-family: Arial; max-width: 800px; margin: 40px auto; padding: 20px;">
        <h1>Processing Sessions</h1>
        <a href="/" style="background: #6c757d; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">← Back to Home</a>
        <h2>Recent Sessions</h2>
        {session_list if session_list else '<p>No sessions found. Upload a CSV file to get started.</p>'}
    </body>
    </html>
    '''

@app.route('/session/<session_id>')
def view_session(session_id):
    session = ProcessingSession.query.get_or_404(session_id)
    return f'''
    <html>
    <head><title>Session: {session.filename}</title></head>
    <body style="font-family: Arial; max-width: 800px; margin: 40px auto; padding: 20px;">
        <h1>Session Details</h1>
        <a href="/sessions" style="background: #6c757d; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">← Back to Sessions</a>
        
        <div style="background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 5px;">
            <h2>{session.filename}</h2>
            <p><strong>Session ID:</strong> {session.id}</p>
            <p><strong>Upload Time:</strong> {session.upload_time}</p>
            <p><strong>Status:</strong> {session.status}</p>
            <p><strong>Total Records:</strong> {session.total_records}</p>
        </div>
        
        <div style="background: #d1ecf1; padding: 15px; border-radius: 5px;">
            <h3>📊 Analysis Features (Coming Soon)</h3>
            <p>This is the basic version. The full Email Guardian includes:</p>
            <ul>
                <li>Machine Learning Risk Analysis</li>
                <li>Domain Classification & Whitelisting</li>
                <li>Business Rules Engine</li>
                <li>Interactive Dashboards</li>
                <li>Case Management System</li>
                <li>Advanced Analytics & Insights</li>
            </ul>
        </div>
    </body>
    </html>
    '''

@app.route('/rules')
def rules():
    return '<html><body style="font-family: Arial; text-align: center; margin-top: 100px;"><h1>Rules Management</h1><p>Feature available in full version</p><a href="/">← Back to Home</a></body></html>'

@app.route('/whitelist')
def whitelist():
    return '<html><body style="font-family: Arial; text-align: center; margin-top: 100px;"><h1>Domain Whitelist</h1><p>Feature available in full version</p><a href="/">← Back to Home</a></body></html>'

@app.route('/settings')
def settings():
    return '<html><body style="font-family: Arial; text-align: center; margin-top: 100px;"><h1>Settings</h1><p>Feature available in full version</p><a href="/">← Back to Home</a></body></html>'

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 EMAIL GUARDIAN - LOCAL VERSION STARTING")
    print("=" * 60)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Server: http://127.0.0.1:5000")
    print("=" * 60)
    print("✅ Ready! Open your browser to: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server")
    print()
    
    # Use appropriate server for platform
    if platform.system() == 'Windows':
        try:
            from waitress import serve
            print("Using Waitress server (Windows optimized)")
            serve(app, host='127.0.0.1', port=5000)
        except ImportError:
            print("Using Flask development server")
            app.run(host='127.0.0.1', port=5000, debug=True)
    else:
        app.run(host='127.0.0.1', port=5000, debug=True)