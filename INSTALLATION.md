# Email Guardian - Local Installation Guide

## Quick Installation

### 1. Download Required Files
Download these 4 files to a new folder:
- `setup.py` - Installation script
- `local_standalone.py` - Main application
- `requirements_local.txt` - Dependencies list
- `README.md` - Documentation

### 2. Install Dependencies
**Option A - Automatic (Recommended):**
```bash
python setup.py
```

**Option B - Manual:**
```bash
pip install -r requirements_local.txt
```

### 3. Run Application
**Windows:**
```bash
python local_standalone.py
# OR double-click run.bat
```

**Mac/Linux:**
```bash
python3 local_standalone.py
# OR run ./run.sh
```

### 4. Access Interface
Open browser to: **http://127.0.0.1:5000**

## System Requirements
- Python 3.8 or higher
- 4GB RAM minimum
- 1GB storage space
- Modern web browser

## Features
- CSV file upload and processing
- Session management
- Database storage (SQLite)
- Web-based interface
- Windows/Mac/Linux compatible

## Troubleshooting
- **Python not found**: Install from python.org
- **Permission errors**: Run as administrator
- **Port 5000 busy**: Kill other processes using port 5000
- **Package install fails**: Use `pip install --user package_name`

## Files Created
```
email-guardian/
├── setup.py
├── local_standalone.py
├── requirements.txt
├── uploads/              # Created automatically
├── data/                 # Created automatically
└── local_email_guardian.db  # Created on first run
```