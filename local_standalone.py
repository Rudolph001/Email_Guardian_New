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
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local_email_guardian.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Add proxy fix for proper URL generation
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize database with app
db.init_app(app)

# Ensure upload directories exist
os.makedirs('uploads', exist_ok=True)
os.makedirs('data', exist_ok=True)

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

class WhitelistDomain(db.Model):
    __tablename__ = 'whitelist_domains'
    
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), nullable=False, unique=True, index=True)
    domain_type = db.Column(db.String(50), default='Corporate')  # Corporate, Personal, Public, Partner
    added_by = db.Column(db.String(100), default='Admin')
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(Text)
    is_active = db.Column(db.Boolean, default=True, index=True)
    
    def __repr__(self):
        return f'<WhitelistDomain {self.domain}>'

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

@app.route('/dashboard/<session_id>')
def dashboard(session_id):
    """Basic dashboard for session - simplified version"""
    session = ProcessingSession.query.get_or_404(session_id)
    return render_template('dashboard.html', session=session, session_id=session_id)

@app.route('/admin')
def admin():
    """Admin panel for system configuration"""
    stats = {
        'total_sessions': ProcessingSession.query.count(),
        'active_sessions': ProcessingSession.query.filter_by(status='processing').count(),
        'completed_sessions': ProcessingSession.query.filter_by(status='completed').count(),
        'failed_sessions': ProcessingSession.query.filter_by(status='failed').count()
    }
    recent_sessions = ProcessingSession.query.order_by(ProcessingSession.upload_time.desc()).limit(5).all()
    return render_template('admin.html', stats=stats, recent_sessions=recent_sessions)

@app.route('/rules')
def rules():
    """Rules management page"""
    return render_template('rules.html')

@app.route('/whitelist-domains')
def whitelist_domains():
    """Whitelist domains management interface"""
    return render_template('whitelist_domains.html')

@app.route('/api/whitelist-domains', methods=['GET', 'POST'])
def api_whitelist_domains():
    """Get all whitelist domains or create new one"""
    if request.method == 'GET':
        domains = WhitelistDomain.query.order_by(WhitelistDomain.added_at.desc()).all()
        return jsonify([{
            'id': domain.id,
            'domain': domain.domain,
            'domain_type': domain.domain_type,
            'added_by': domain.added_by,
            'added_at': domain.added_at.isoformat() if domain.added_at else None,
            'notes': domain.notes,
            'is_active': domain.is_active
        } for domain in domains])

    elif request.method == 'POST':
        try:
            data = request.get_json() or {}
            domain_name = data.get('domain', '').strip().lower()
            
            if not domain_name:
                return jsonify({'success': False, 'message': 'Domain is required'}), 400
            
            # Check if domain already exists
            existing = WhitelistDomain.query.filter_by(domain=domain_name).first()
            if existing:
                return jsonify({'success': False, 'message': f'Domain {domain_name} already exists'}), 400
            
            whitelist_domain = WhitelistDomain(
                domain=domain_name,
                domain_type=data.get('domain_type', 'Corporate'),
                added_by=data.get('added_by', 'Admin'),
                notes=data.get('notes', '')
            )
            
            db.session.add(whitelist_domain)
            db.session.commit()
            
            return jsonify({'success': True, 'message': f'Domain {domain_name} added successfully', 'id': whitelist_domain.id})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/whitelist-domains/<int:domain_id>/toggle', methods=['POST'])
def api_toggle_whitelist_domain(domain_id):
    """Toggle whitelist domain active status"""
    try:
        domain = WhitelistDomain.query.get_or_404(domain_id)
        domain.is_active = not domain.is_active
        db.session.commit()
        
        status = 'activated' if domain.is_active else 'deactivated'
        
        return jsonify({
            'success': True, 
            'message': f'Domain {domain.domain} {status} successfully',
            'is_active': domain.is_active
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/whitelist-domains/<int:domain_id>', methods=['DELETE'])
def api_delete_whitelist_domain(domain_id):
    """Delete whitelist domain"""
    try:
        domain = WhitelistDomain.query.get_or_404(domain_id)
        domain_name = domain.domain
        db.session.delete(domain)
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Domain {domain_name} deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Initialize the database
with app.app_context():
    db.create_all()
    
    # Add default whitelist domains if none exist
    if WhitelistDomain.query.count() == 0:
        print("Adding default whitelist domains...")
        default_domains = [
            {'domain': 'company.com', 'domain_type': 'Corporate', 'notes': 'Default corporate domain'},
            {'domain': 'corp.com', 'domain_type': 'Corporate', 'notes': 'Default corporate domain'},
            {'domain': 'trusted-partner.com', 'domain_type': 'Corporate', 'notes': 'Trusted business partner'}
        ]
        
        for domain_data in default_domains:
            domain = WhitelistDomain(**domain_data)
            db.session.add(domain)
        
        db.session.commit()
        print(f"Added {len(default_domains)} default whitelist domains")
    
    print("Database tables created successfully!")
    print(f"Application running with professional template system")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version.split()[0]}")

# Only run if called directly (not when imported)
if __name__ == '__main__':
    print()
    print("Email Guardian is ready!")
    print("Access at: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server")
    print()
    app.run(debug=True, host='127.0.0.1', port=5000)