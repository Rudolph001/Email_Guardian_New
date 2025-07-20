# Email Guardian - Local Installation with Professional UI

## Overview
Your local version now uses the same professional template system as the Replit deployment, featuring:
- Bootstrap 5 responsive design
- Custom CSS styling with professional theme
- Font Awesome icons
- Chart.js visualizations
- DataTables for enhanced data display
- Interactive dashboard animations

## Installation Instructions

### 1. Install Dependencies

**For Windows users with compiler issues:**
```bash
pip install -r requirements_minimal.txt
```

**For full features (requires C++ compiler):**
```bash
pip install -r requirements_local.txt
```

### 2. Run the Application
```bash
python local_standalone.py
```

### 3. Access the Application
Open your browser to: http://127.0.0.1:5000

## Features Available Locally

### Professional UI Components
- ✅ Bootstrap 5 responsive design
- ✅ Custom CSS with business theme
- ✅ Font Awesome icons
- ✅ Interactive file upload with drag & drop
- ✅ Professional navigation with dropdown menus
- ✅ Animated dashboard cards and counters
- ✅ Chart.js visualizations
- ✅ DataTables with sorting and filtering

### Core Functionality
- ✅ CSV file processing
- ✅ Machine learning analysis
- ✅ Risk assessment and scoring
- ✅ Domain classification and whitelisting
- ✅ Case management system
- ✅ Rule engine for custom business logic
- ✅ Multiple specialized dashboards
- ✅ Advanced analytics and reporting

### Database
- SQLite database stored in `instance/local_email_guardian.db`
- Automatic table creation on first run
- Session-based data management

## File Structure for Local Installation
```
email-guardian/
├── local_standalone.py      # Application launcher
├── local_app.py            # Local Flask configuration
├── local_models.py         # Model compatibility layer
├── requirements_local.txt  # Local dependencies
├── app.py                  # Main app configuration
├── models.py              # Database models
├── routes.py              # Web routes and endpoints
├── templates/             # HTML templates (Bootstrap UI)
├── static/                # CSS/JS assets
├── uploads/               # CSV file uploads
├── data/                  # Session data storage
└── instance/              # SQLite database directory
```

## Key Differences from Simple Version
The previous simple version (`local_standalone_old.py`) used inline HTML with basic styling. The new version uses:

1. **Professional Templates**: Full Jinja2 template system with layout inheritance
2. **Bootstrap Framework**: Responsive design with modern UI components
3. **Custom Styling**: Professional business theme with consistent branding
4. **Interactive Features**: JavaScript-powered animations and user interactions
5. **Advanced Components**: Charts, data tables, and dashboard widgets

## Troubleshooting

### If you get import errors:
```bash
# Make sure you're in the correct directory
cd path/to/email-guardian

# Install dependencies
pip install -r requirements_local.txt

# If you still get circular import errors, use the standalone version:
python local_standalone.py
```

### Note on Standalone vs Full Version
- `local_standalone.py` - Simplified version with professional UI (recommended for local use)
- `local_app.py` - Full featured version that mirrors Replit deployment exactly

### If templates are not found:
Make sure the `templates/` and `static/` directories are in the same folder as your Python files.

### For Windows users:
The application will automatically try to use Waitress server for better performance:
```bash
pip install waitress
```

## Development Mode
The local version runs in debug mode by default, which provides:
- Automatic reloading when files change
- Detailed error messages
- Interactive debugger in browser

## Production Deployment
For production use, modify `local_app.py`:
1. Set `DEBUG = False`
2. Use a strong secret key
3. Consider using PostgreSQL instead of SQLite
4. Use a production WSGI server like Gunicorn

Your local Email Guardian installation now provides the same professional experience as the cloud deployment!