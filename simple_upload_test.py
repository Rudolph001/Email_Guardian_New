#!/usr/bin/env python3
"""
Simple Mac upload test - bypasses JavaScript entirely
This creates a minimal upload form that works without any JavaScript validation
"""

from flask import Flask, request, redirect, url_for, flash, render_template_string
import os
import sys

# Add current directory to path
sys.path.insert(0, '.')

# Simple HTML template without JavaScript complications
SIMPLE_UPLOAD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Simple CSV Upload Test</title>
    <style>
        body { font-family: Arial; margin: 50px; }
        .upload-area { border: 2px dashed #ccc; padding: 50px; text-align: center; margin: 20px 0; }
        .btn { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
        .alert { padding: 15px; margin: 10px 0; border-radius: 4px; }
        .alert-success { background: #d4edda; color: #155724; }
        .alert-error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <h1>Simple CSV Upload Test for Mac</h1>
    
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ category }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    
    <div class="upload-area">
        <form action="/simple-upload" method="post" enctype="multipart/form-data">
            <h3>Upload CSV File</h3>
            <input type="file" name="file" accept=".csv" required>
            <br><br>
            <button type="submit" class="btn">Upload CSV</button>
        </form>
    </div>
    
    <div>
        <h3>Instructions:</h3>
        <ol>
            <li>Select your CSV file</li>
            <li>Click Upload CSV</li>
            <li>Wait for processing to complete</li>
        </ol>
        
        <p><strong>Note:</strong> This is a simplified upload test that bypasses JavaScript validation.</p>
        <p><a href="/">Return to main application</a></p>
    </div>
</body>
</html>
'''

def create_simple_upload_app():
    """Create a simple Flask app for testing uploads"""
    from app import app, db
    from routes import data_processor
    from models import ProcessingSession
    import uuid
    from datetime import datetime
    
    @app.route('/simple-upload-test')
    def simple_upload_page():
        """Simple upload page without JavaScript"""
        return render_template_string(SIMPLE_UPLOAD_TEMPLATE)
    
    @app.route('/simple-upload', methods=['POST'])
    def simple_upload():
        """Handle simple upload without JavaScript validation"""
        try:
            if 'file' not in request.files:
                flash('No file selected', 'error')
                return redirect(url_for('simple_upload_page'))
            
            file = request.files['file']
            
            if not file.filename:
                flash('No file selected', 'error')
                return redirect(url_for('simple_upload_page'))
            
            if not file.filename.lower().endswith('.csv'):
                flash('Please select a CSV file', 'error')
                return redirect(url_for('simple_upload_page'))
            
            # Create session ID
            session_id = str(uuid.uuid4())
            filename = file.filename
            
            # Save file
            upload_dir = 'uploads'
            os.makedirs(upload_dir, exist_ok=True)
            
            # Simple filename sanitization
            safe_filename = filename.replace(' ', '_').replace('(', '').replace(')', '')
            upload_path = os.path.join(upload_dir, f"{session_id}_{safe_filename}")
            
            file.save(upload_path)
            
            # Create session record
            session = ProcessingSession()
            session.id = session_id
            session.filename = filename
            session.status = 'uploaded'
            session.upload_time = datetime.utcnow()
            
            db.session.add(session)
            db.session.commit()
            
            # Process the file
            try:
                data_processor.process_csv(session_id, upload_path)
                flash(f'File uploaded and processed successfully! Session ID: {session_id}', 'success')
                
                # Redirect to dashboard
                return redirect(url_for('dashboard', session_id=session_id))
                
            except Exception as processing_error:
                flash(f'Upload succeeded but processing failed: {str(processing_error)}', 'error')
                return redirect(url_for('simple_upload_page'))
            
        except Exception as e:
            flash(f'Upload failed: {str(e)}', 'error')
            return redirect(url_for('simple_upload_page'))
    
    return app

def main():
    """Run simple upload test"""
    print("=== Simple Mac Upload Test ===")
    print("This creates a JavaScript-free upload page for testing")
    
    try:
        app = create_simple_upload_app()
        
        print("Starting simple upload test server...")
        print("Open your browser to: http://localhost:5001/simple-upload-test")
        print("Press Ctrl+C to stop")
        
        # Set Mac environment
        if sys.platform == 'darwin':
            os.environ.setdefault('LC_ALL', 'en_US.UTF-8')
            os.environ.setdefault('LANG', 'en_US.UTF-8')
            os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
        
        app.run(host='0.0.0.0', port=5001, debug=True)
        
    except Exception as e:
        print(f"Error starting test server: {e}")

if __name__ == "__main__":
    main()