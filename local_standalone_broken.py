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