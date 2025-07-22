
# Email Guardian - Local Setup Guide

This guide helps you run Email Guardian on your local Windows or Mac machine.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Quick Start

1. **Debug your environment (RECOMMENDED):**
   ```bash
   python debug_local.py
   ```
   This checks directories, database, and permissions.

2. **Start the application:**
   ```bash
   python local_run.py
   ```

3. **Open your browser to:** http://localhost:5000

## Manual Setup (Alternative)

If the setup script doesn't work, you can set up manually:

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create Directories
```bash
mkdir uploads data instance
```

### 3. Set Environment Variables (Windows)
```cmd
set FLASK_ENV=development
set SESSION_SECRET=your-secret-key
```

### 3. Set Environment Variables (Mac/Linux)
```bash
export FLASK_ENV=development
export SESSION_SECRET=your-secret-key
```

### 4. Run the Application
```bash
python main.py
```

## Production Deployment

For production use:

```bash
gunicorn --bind 0.0.0.0:5000 main:app
```

## Configuration

The application uses these environment variables:

- `SESSION_SECRET`: Flask session secret key
- `DATABASE_URL`: Database connection string (defaults to SQLite)
- `FAST_MODE`: Enable performance optimizations (recommended: true)
- `FLASK_DEBUG`: Enable debug mode for development

## File Structure

```
email-guardian/
├── main.py                 # Application entry point
├── local_setup.py          # Setup script
├── local_run.py            # Development runner
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── app.py                 # Flask app configuration
├── models.py              # Database models
├── routes.py              # Web routes
├── uploads/               # File upload directory
├── data/                  # Session data storage
└── instance/              # SQLite database location
```

## Troubleshooting CSV Upload Errors

If you get 500 errors when uploading CSV files:

### Step 1: Run Debug Script
```bash
python debug_local.py
```
This will check and fix common issues automatically.

### Step 2: Manual Fixes (if needed)

**Missing Dependencies:**
```bash
pip install flask flask-sqlalchemy pandas scikit-learn numpy networkx
```

**Missing Directories:**
```bash
mkdir uploads data instance
```

**Database Reset:**
```bash
rm -f instance/email_guardian.db
python local_run.py  # Will recreate database
```

### Common Error Solutions

- **"No module named 'app'"**: Run from project root directory
- **"Session unavailable"**: SESSION_SECRET now set automatically in local_run.py
- **"Database locked"**: Stop any running instances before restart
- **Upload 500 error**: Check file permissions and run debug_local.py

### Database Issues
The app uses SQLite by default. Database file created automatically in `instance/email_guardian.db`.

### Port Already in Use
If port 5000 is busy, modify the port number in `local_run.py`.

## Support

For persistent issues:
1. Run `python debug_local.py` first
2. Check Python version (3.8+ required)
3. Verify all dependencies installed
4. Ensure directories exist with write permissions
