# Email Guardian - Download Instructions

## Files You Need to Download

To run Email Guardian locally, download ALL of these files to the same folder on your computer:

### 📋 Local Installation Files
- `local_app.py` - Main application entry point
- `local_config.py` - Local configuration settings
- `local_requirements.txt` - Python dependencies list
- `setup_local.py` - Automated setup script
- `README_LOCAL.md` - Complete installation guide
- `run_local.bat` - Windows startup script
- `run_local.sh` - Mac/Linux startup script

### 🔧 Core Application Files
- `models.py` - Database models
- `routes.py` - Web routes and API endpoints
- `data_processor.py` - CSV processing engine
- `ml_engine.py` - Machine learning analysis
- `advanced_ml_engine.py` - Advanced ML analytics
- `rule_engine.py` - Security rules engine
- `domain_manager.py` - Domain classification system
- `session_manager.py` - Session management

### 🎨 Frontend Files
You need to download the entire `templates/` and `static/` folders:

**Templates folder** - Contains all HTML files:
- `templates/base.html`
- `templates/dashboard.html`
- `templates/index.html`
- `templates/cases.html`
- `templates/processing.html`
- `templates/escalations.html`
- (and all other .html files in the templates folder)

**Static folder** - Contains CSS, JavaScript, and assets:
- `static/css/style.css`
- `static/js/main.js`
- (and any other files in the static folder)

## 🚀 Quick Start Steps

1. **Create a new folder** on your computer (e.g., "email-guardian-local")

2. **Download all files** listed above into this folder

3. **Open terminal/command prompt** in this folder

4. **Run the setup**:
   - **Windows**: Double-click `run_local.bat` OR run `python setup_local.py`
   - **If setup fails**: Run `python install_manual.py` then `python local_app.py`
   - **Mac/Linux**: Run `./run_local.sh` OR run `python setup_local.py`

5. **Start the application**:
   - **Windows**: Double-click `run_local.bat` OR run `python local_app.py`
   - **Mac/Linux**: Run `./run_local.sh` OR run `python local_app.py`

6. **Open your browser** to: `http://127.0.0.1:5000`

## ✅ Requirements

- **Python 3.8+** installed on your computer
- **4GB RAM minimum** (8GB recommended)
- **1GB free disk space**
- **Internet connection** for initial setup (to download Python packages)

## 📁 Final Folder Structure

Your folder should look like this:
```
email-guardian-local/
├── local_app.py
├── local_config.py
├── local_requirements.txt
├── setup_local.py
├── README_LOCAL.md
├── run_local.bat
├── run_local.sh
├── models.py
├── routes.py
├── data_processor.py
├── ml_engine.py
├── advanced_ml_engine.py
├── rule_engine.py
├── domain_manager.py
├── session_manager.py
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── index.html
│   └── [all other .html files]
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## 🔍 Troubleshooting

If you encounter any issues:

1. **Check Python Installation**: Run `python --version` in terminal
2. **Read the Logs**: Look at the console output for error messages
3. **Check File Permissions**: Make sure all files are in the same folder
4. **Review README_LOCAL.md**: Contains detailed troubleshooting guide

## 📞 Need Help?

If you have issues with the local installation, check the README_LOCAL.md file for detailed troubleshooting steps and configuration options.