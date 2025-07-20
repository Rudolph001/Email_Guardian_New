# Email Guardian - Simple Local Starter
# Use this if local_app.py has import issues

import os
import sys
from flask import Flask, render_template, request, redirect, url_for, flash

# Simple Flask app for testing
app = Flask(__name__)
app.secret_key = 'dev-secret-key'

@app.route('/')
def index():
    return '''
    <html>
    <head><title>Email Guardian - Local Version</title></head>
    <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px;">
        <h1>📧 Email Guardian - Local Installation</h1>
        <div style="background: #e7f5e7; padding: 20px; border-radius: 5px; margin: 20px 0;">
            <h2>✅ Success! Email Guardian is running locally</h2>
            <p>Your local installation is working correctly.</p>
        </div>
        
        <h3>🔧 Setup Status</h3>
        <ul>
            <li>✅ Flask web server running</li>
            <li>✅ Python environment working</li>
            <li>✅ Local server accessible</li>
        </ul>
        
        <h3>📁 Required Files</h3>
        <p>To get the full Email Guardian functionality, make sure you have these files in the same directory:</p>
        <ul>
            <li>models.py - Database models</li>
            <li>routes.py - Web routes and API endpoints</li>
            <li>data_processor.py - CSV processing</li>
            <li>ml_engine.py - Machine learning analysis</li>
            <li>templates/ folder - HTML templates</li>
            <li>static/ folder - CSS and JavaScript</li>
        </ul>
        
        <h3>🚀 Next Steps</h3>
        <ol>
            <li>Download all project files to this directory</li>
            <li>Run: <code>python install_manual.py</code></li>
            <li>Then run: <code>python local_app.py</code></li>
        </ol>
        
        <div style="background: #f0f8ff; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h4>📊 Current Directory Contents:</h4>
            <ul>''' + ''.join([f'<li>{file}</li>' for file in sorted(os.listdir('.')) if not file.startswith('.')]) + '''</ul>
        </div>
        
        <p><strong>Server Info:</strong> Running on http://127.0.0.1:5000</p>
        <p><strong>Python Version:</strong> ''' + sys.version + '''</p>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("Starting Email Guardian Simple Test Server...")
    print("Open your browser to: http://127.0.0.1:5000")
    print("This is a basic test to verify your setup is working.")
    print("Press Ctrl+C to stop")
    
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True
    )