
# Email Guardian - Local Setup Guide

This guide helps you run Email Guardian on your local Windows or Mac machine.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Quick Start

1. **Run the setup script:**
   ```bash
   python local_setup.py
   ```

2. **Configure environment (optional):**
   ```bash
   cp .env.example .env
   # Edit .env file with your preferences
   ```

3. **Start the application:**
   ```bash
   python local_run.py
   ```
   
   Or use the original entry point:
   ```bash
   python main.py
   ```

4. **Open your browser to:** http://localhost:5000

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

## Troubleshooting

### Database Issues
The app uses SQLite by default, which requires no additional setup. The database file will be created automatically in `instance/email_guardian.db`.

### Port Already in Use
If port 5000 is busy, you can change it by modifying the port number in `main.py` or `local_run.py`.

### Missing Dependencies
Run `pip install -r requirements.txt` to install all required packages.

## Support

For issues with local setup, check:
1. Python version (3.8+ required)
2. All dependencies installed
3. Required directories exist
4. Environment variables set correctly
