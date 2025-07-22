#!/bin/bash
# Mac-optimized Email Guardian startup script

echo "🍎 Starting Email Guardian with Mac optimizations..."

# Set Mac-friendly environment variables
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
export PYTHONIOENCODING=utf-8

# Create necessary directories
mkdir -p uploads data instance

# Set file permissions
chmod 755 uploads data instance
find uploads -type f -exec chmod 644 {} \; 2>/dev/null || true

echo ""
echo "⚠️  IMPORTANT: Use Chrome browser on Mac, not Safari!"
echo "   Safari has compatibility issues with file uploads."
echo ""

# Start the application
echo "Starting Email Guardian..."
echo "Open Chrome browser and go to: http://localhost:5000"
echo ""

python3 local_run.py