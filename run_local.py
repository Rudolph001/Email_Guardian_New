#!/usr/bin/env python3
"""
Simple local runner for Email Guardian
Optimized for local development with minimal setup
"""

import os
import sys
from pathlib import Path

# Set environment variables before importing app
os.environ['SESSION_SECRET'] = 'local-dev-secret-key-email-guardian-2025'
os.environ['DATABASE_URL'] = 'sqlite:///instance/email_guardian.db'
os.environ['FAST_MODE'] = 'true'
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = 'true'

# Create directories
Path('instance').mkdir(exist_ok=True)
Path('uploads').mkdir(exist_ok=True)
Path('data').mkdir(exist_ok=True)

print("=== Email Guardian Local Development ===")
print("Setting up local environment...")
print(f"Database: {os.environ['DATABASE_URL']}")
print("Starting server on http://localhost:5000")
print("Press Ctrl+C to stop")
print("=========================================")

# Import and run the app
from app import app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=True)