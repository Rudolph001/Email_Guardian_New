# Mac CSV Upload Fixes for Email Guardian

This document describes the fixes applied to resolve CSV upload issues on Mac systems.

## Problem
Users on Mac were encountering a JavaScript error "unknownUploadURL_Title" when trying to upload CSV files, preventing successful file uploads.

## Root Cause
The issue was caused by browser-specific JavaScript validation that was incompatible with Mac Safari/Chrome, combined with strict file validation that interfered with the upload process.

## Solutions Applied

### 1. Enhanced Upload Form (`templates/index.html`)
- Added `novalidate` attribute to disable browser validation
- Enhanced error handling for cross-platform compatibility
- Improved file validation messaging

### 2. Mac-Specific JavaScript (`static/js/mac-upload-fix.js`)
- Created dedicated Mac upload handling script
- Simplified file validation and display
- Enhanced drag-and-drop functionality
- Added fallback error handling for "unknownUploadURL" errors
- Improved cross-platform file handling

### 3. Simplified Upload Test (`simple_upload_test.py`)
- Created JavaScript-free upload test page
- Bypasses all browser validation issues
- Direct server-side processing
- Useful for debugging upload problems

### 4. Enhanced Error Handling (`routes.py`)
- Improved background processing error handling
- Better session management
- Enhanced logging for debugging

### 5. Cross-Platform CSV Processing (`data_processor.py`)
- Multiple encoding support (UTF-8, UTF-8-sig, macroman, iso-8859-1, cp1252)
- Automatic encoding detection using chardet
- Mac-specific file handling improvements

## Usage Instructions

### Method 1: Use the Fixed Main Application
1. Start the application: `python3 local_run.py`
2. Open browser: `http://localhost:5000`
3. Upload CSV files using the enhanced interface

### Method 2: Use the Simple Upload Test (Recommended for troubleshooting)
1. Run the test: `python3 simple_upload_test.py`
2. Open browser: `http://localhost:5001/simple-upload-test`
3. Use the JavaScript-free upload form

### Method 3: Use Mac Optimization Scripts
1. Apply all fixes: `python3 fix_mac_upload.py`
2. Start with Mac settings: `./start_mac.sh`
3. Debug if needed: `python3 debug_mac_upload.py`

## Environment Variables for Mac
```bash
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
export PYTHONIOENCODING=utf-8
```

## File Export Instructions for Mac Users
When exporting CSV files from Excel on Mac:
1. Choose "File → Export → CSV UTF-8 (Comma delimited)"
2. Ensure file permissions: `chmod 644 your_file.csv`
3. Avoid special characters in filenames

## Troubleshooting

### If upload still fails:
1. Run: `python3 debug_mac_upload.py`
2. Check file permissions: `ls -la your_file.csv`
3. Try the simple upload test: `python3 simple_upload_test.py`
4. Check console logs in browser developer tools

### Common Issues:
- **File permissions**: Ensure CSV file is readable (644 permissions)
- **File encoding**: Use UTF-8 encoding when exporting CSV
- **File size**: Keep files under 500MB
- **Filename**: Avoid special characters in filenames

## Technical Details

### JavaScript Error Prevention
The "unknownUploadURL" error was caused by:
- Browser validation conflicts
- Missing error handling for file URL generation
- Cross-platform JavaScript incompatibilities

### Fixed by:
- Adding `novalidate` to form
- Enhanced error handling in `mac-upload-fix.js`
- Fallback upload methods
- Improved file validation

### Encoding Support
Added support for multiple encodings commonly used on Mac:
- UTF-8 (standard)
- UTF-8-sig (with BOM)
- macroman (legacy Mac encoding)
- iso-8859-1 (Western European)
- cp1252 (Windows encoding, often used in Mac Office)

## Files Modified
- `templates/index.html` - Enhanced upload form
- `templates/base.html` - Added Mac upload script
- `static/js/mac-upload-fix.js` - New Mac-specific JavaScript
- `routes.py` - Improved error handling
- `data_processor.py` - Cross-platform CSV processing
- `simple_upload_test.py` - JavaScript-free upload test

## Testing
All fixes have been tested with:
- Mac Safari and Chrome browsers
- Various CSV file encodings
- Different file sizes and formats
- Drag-and-drop and click-to-browse upload methods