# Email Guardian - Local Installation Guide

## Quick Start

1. **Download the application files** to your local machine
2. **Run the setup script**: `python setup_local.py`
3. **Start the application**: `python local_app.py`
4. **Open your browser** to: `http://127.0.0.1:5000`

## System Requirements

- **Python 3.8+** (Python 3.9 or 3.10 recommended)
- **Windows, macOS, or Linux**
- **4GB RAM minimum** (8GB recommended for large datasets)
- **1GB free disk space**

## Installation Steps

### Step 1: Download Files
Download all the following files to a single directory on your machine:

**Core Application Files:**
- `local_app.py` - Main application entry point
- `local_config.py` - Local configuration
- `local_requirements.txt` - Python dependencies
- `setup_local.py` - Automated setup script

**Application Logic Files:**
- `models.py` - Database models
- `routes.py` - Web routes and API endpoints
- `data_processor.py` - CSV processing engine
- `ml_engine.py` - Machine learning analysis
- `advanced_ml_engine.py` - Advanced ML analytics
- `rule_engine.py` - Security rules engine
- `domain_manager.py` - Domain classification
- `session_manager.py` - Session management

**Frontend Files:**
- `templates/` folder - All HTML templates
- `static/` folder - CSS, JavaScript, and assets

### Step 2: Run Setup Script

**Option A - Automatic Setup:**
```bash
python setup_local.py
```

**Option B - If setup fails (Windows Python 3.13+):**
```bash
python install_manual.py
python local_app.py
```

**Option C - Manual Installation:**
```bash
pip install Flask Flask-SQLAlchemy pandas numpy scikit-learn networkx email-validator waitress
python local_app.py
```

The setup will:
- Check Python version compatibility
- Install required packages
- Create necessary directories
- Set up the SQLite database
- Create environment configuration

### Step 3: Start the Application
```bash
python local_app.py
```

The application will start on `http://127.0.0.1:5000`

## Configuration Options

### Database Configuration
By default, the application uses SQLite for local development. To use PostgreSQL:

1. Install PostgreSQL locally
2. Uncomment the PostgreSQL line in `local_requirements.txt`
3. Update the database URL in `.env` file:
   ```
   DATABASE_URL=postgresql://username:password@localhost/email_guardian
   ```

### Performance Settings
Edit `local_config.py` to adjust:
- `MAX_CONTENT_LENGTH` - Maximum upload file size
- `MAX_RECORDS_PER_SESSION` - Maximum records per analysis
- `ITEMS_PER_PAGE` - Pagination settings

## Directory Structure
```
email-guardian-local/
├── local_app.py              # Application entry point
├── local_config.py           # Configuration settings
├── local_requirements.txt    # Python dependencies
├── setup_local.py           # Setup automation
├── models.py                # Database models
├── routes.py                # Web routes
├── data_processor.py        # Data processing
├── ml_engine.py            # ML analysis
├── advanced_ml_engine.py   # Advanced analytics
├── rule_engine.py          # Security rules
├── domain_manager.py       # Domain management
├── session_manager.py      # Session handling
├── uploads/                # CSV file uploads
├── data/                   # Session data storage
├── instance/               # Database files
├── static/                 # Web assets
│   ├── css/
│   └── js/
├── templates/              # HTML templates
└── local_email_guardian.db # SQLite database
```

## Usage Guide

### 1. Upload Email Data
- Navigate to the home page
- Upload a CSV file with email export data
- Supported formats: Tessian export format or standard email CSV

### 2. Data Processing
- The system automatically processes uploaded data
- Applies exclusion rules, whitelist filtering, and ML analysis
- Progress is shown in real-time

### 3. Analysis Dashboards
- **Main Dashboard**: Overview with animated statistics
- **Case Management**: Review flagged emails
- **Sender Analysis**: Analyze communication patterns
- **Time Analysis**: Temporal analysis of email activity
- **Advanced ML**: Machine learning insights

### 4. Domain Whitelisting
- Manage trusted domains
- Automatic whitelist recommendations
- Bulk domain operations

## Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Find process using port 5000
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# Kill the process or use a different port
python local_app.py --port 5001
```

**Database Errors**
```bash
# Reset the database
rm local_email_guardian.db
python local_app.py
```

**Import Errors**
- Ensure all files are in the same directory
- Check that virtual environment is activated
- Reinstall requirements: `pip install -r local_requirements.txt`

**Memory Issues with Large Files**
- Reduce `MAX_RECORDS_PER_SESSION` in `local_config.py`
- Process files in smaller chunks
- Increase system memory or use a more powerful machine

### Performance Optimization

**For Large Datasets:**
1. Use PostgreSQL instead of SQLite
2. Increase system RAM
3. Use SSD storage
4. Adjust chunk size in data processing

**For Production Use:**
1. Use Gunicorn: `gunicorn --bind 0.0.0.0:5000 local_app:app`
2. Set up reverse proxy (Nginx)
3. Configure proper logging
4. Use environment variables for secrets

## Security Considerations

### Local Development
- Default configuration is for development only
- Change the `SESSION_SECRET` in production
- Use HTTPS in production environments
- Restrict file upload types and sizes

### Data Privacy
- All data is processed locally on your machine
- No data is sent to external servers
- Email content remains on your local system
- Regular cleanup of temporary files recommended

## Advanced Configuration

### Environment Variables
Create a `.env` file with:
```
DATABASE_URL=sqlite:///local_email_guardian.db
SESSION_SECRET=your-secret-key-here
UPLOAD_FOLDER=uploads
DATA_FOLDER=data
MAX_CONTENT_LENGTH=104857600
```

### Custom Rules
Edit security rules by creating JSON configuration files in the `data/` directory.

### ML Model Tuning
Adjust ML parameters in `ml_engine.py` and `advanced_ml_engine.py` for your specific use case.

## Support

For issues with local installation:
1. Check the console output for error messages
2. Ensure all required files are present
3. Verify Python version and dependencies
4. Check system resources (RAM, disk space)

## License

Email Guardian is designed for enterprise email security analysis. Ensure compliance with your organization's data handling policies when processing email data.