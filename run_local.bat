@echo off
REM Email Guardian - Windows Batch Script for Local Execution

echo.
echo ====================================
echo  Email Guardian - Local Startup
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if setup has been run
if not exist "local_email_guardian.db" (
    echo Setting up Email Guardian for first run...
    python setup_local.py
    if errorlevel 1 (
        echo Setup failed. Please check the error messages above.
        pause
        exit /b 1
    )
)

REM Start the application
echo.
echo Starting Email Guardian...
echo Open your browser to: http://127.0.0.1:5000
echo Press Ctrl+C to stop the server
echo.

python local_app.py

pause