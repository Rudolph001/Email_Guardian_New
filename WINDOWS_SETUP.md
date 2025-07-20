# Email Guardian - Windows Setup Guide

## Quick Start (Minimal Setup)

Since you're getting compiler errors with the full data science stack, let's start with the basic version:

### 1. Install Minimal Dependencies
```bash
pip install -r requirements_minimal.txt
```

OR install manually:
```bash
pip install flask flask-sqlalchemy waitress
```

### 2. Run the Application
```bash
python local_standalone.py
```

### 3. Access the App
Open your browser to: http://127.0.0.1:5000

## What You'll Get

✅ **Professional Bootstrap UI** - Same beautiful interface as Replit  
✅ **File Upload System** - CSV file upload with drag & drop  
✅ **Session Management** - Track uploaded files  
✅ **SQLite Database** - Automatic database creation  
✅ **Responsive Design** - Works on all screen sizes  

## If You Want Full Analytics (Optional)

The data science features (pandas, numpy, scikit-learn) require a C++ compiler on Windows. If you want the full analytics:

### Option 1: Install Visual Studio Build Tools
1. Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Install "C++ build tools"
3. Then run: `pip install -r requirements_local.txt`

### Option 2: Use Anaconda/Miniconda
1. Install Anaconda: https://www.anaconda.com/download
2. Create environment: `conda create -n emailguard python=3.11`
3. Activate: `conda activate emailguard`
4. Install: `conda install flask flask-sqlalchemy pandas numpy scikit-learn`

## Troubleshooting

### If you get "module not found" errors:
```bash
# Make sure you're in the right directory
cd path\to\Email_Guardian_New

# Check if Flask is installed
python -c "import flask; print('Flask installed successfully')"
```

### If the browser shows errors:
- Make sure the `templates` and `static` folders are in the same directory as `local_standalone.py`
- Check the console output for any error messages

## File Structure Check
Make sure you have these files/folders:
```
Email_Guardian_New/
├── local_standalone.py      ← Run this file
├── templates/               ← HTML templates
├── static/                  ← CSS/JS files  
├── requirements_minimal.txt ← Basic dependencies
└── instance/               ← Database folder (created automatically)
```

The basic version will give you the beautiful interface without needing the complex data science libraries!