#!/bin/bash
# Email Guardian - Unix/Linux/macOS Shell Script for Local Execution

echo ""
echo "===================================="
echo " Email Guardian - Local Startup"
echo "===================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python is not installed"
        echo "Please install Python 3.8+ from your package manager or https://python.org"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Display Python version
echo "Python version: $($PYTHON_CMD --version)"

# Check if setup has been run
if [ ! -f "local_email_guardian.db" ]; then
    echo "Setting up Email Guardian for first run..."
    $PYTHON_CMD setup_local.py
    if [ $? -ne 0 ]; then
        echo "Setup failed. Please check the error messages above."
        exit 1
    fi
fi

# Start the application
echo ""
echo "Starting Email Guardian..."
echo "Open your browser to: http://127.0.0.1:5000"
echo "Press Ctrl+C to stop the server"
echo ""

$PYTHON_CMD local_app.py