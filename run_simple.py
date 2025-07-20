# Email Guardian - Simple Runner (No Dependencies)
# Use this to avoid all import issues

import os
import sys
from flask import Flask

# Create simple Flask app
app = Flask(__name__)
app.secret_key = 'simple-test-key'

@app.route('/')
def home():
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Email Guardian - Working!</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
            .success {{ background: #d4edda; padding: 20px; border-radius: 5px; color: #155724; }}
            .info {{ background: #d1ecf1; padding: 15px; border-radius: 5px; color: #0c5460; margin: 10px 0; }}
            .code {{ background: #f8f9fa; padding: 10px; border-radius: 3px; font-family: monospace; }}
        </style>
    </head>
    <body>
        <h1>📧 Email Guardian - Local Installation Test</h1>
        
        <div class="success">
            <h2>✅ Success! Your setup is working</h2>
            <p>Flask is running properly on your Windows Python 3.13 system.</p>
        </div>
        
        <div class="info">
            <h3>System Information</h3>
            <p><strong>Python Version:</strong> {sys.version}</p>
            <p><strong>Current Directory:</strong> {os.getcwd()}</p>
            <p><strong>Server:</strong> http://127.0.0.1:5000</p>
        </div>
        
        <div class="info">
            <h3>Files in Current Directory</h3>
            <div class="code">
                {'<br>'.join(sorted([f for f in os.listdir('.') if not f.startswith('.') and f.endswith('.py')]))}
            </div>
        </div>
        
        <div class="info">
            <h3>Next Steps</h3>
            <ol>
                <li>This confirms your Python and Flask setup works</li>
                <li>Try installing packages: <code>python install_manual.py</code></li>
                <li>Then run the full app: <code>python local_app.py</code></li>
            </ol>
        </div>
        
        <p><em>Press Ctrl+C in the terminal to stop this server</em></p>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("Email Guardian Simple Test - Starting...")
    print("Open browser: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop")
    app.run(host='127.0.0.1', port=5000, debug=True)