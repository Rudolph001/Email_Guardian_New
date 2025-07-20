#!/usr/bin/env python3
"""
Email Guardian - Local Application Launcher
Uses the professional template system with Bootstrap and custom CSS
"""

print("Starting Email Guardian with professional template system...")
print("This version uses the same beautiful interface as the Replit deployment.")
print()

# Import the local app configuration
from local_app import app

if __name__ == '__main__':
    print("Email Guardian is ready!")
    print("Access at: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server")
    print()
    app.run(debug=True, host='127.0.0.1', port=5000)
                    <strong>📊 Expected Columns:</strong> sender, subject, recipients, attachments, timestamps
                </div>
                <input type="file" name="file" accept=".csv" required style="padding: 10px; margin-right: 10px; border: 1px solid #ddd; border-radius: 3px;">
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