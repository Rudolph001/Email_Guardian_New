# Mac CSV Upload Fixes for Email Guardian

## Issue Resolved
CSV file uploads work on Windows but fail on Mac systems due to encoding and file handling differences.

## Solution Implemented

### 1. Enhanced Cross-Platform File Handling
- **Automatic Encoding Detection**: Uses `chardet` library to detect file encoding
- **Multiple Encoding Support**: Supports UTF-8, UTF-8-sig, macroman, iso-8859-1, cp1252
- **Graceful Fallbacks**: If one encoding fails, automatically tries the next

### 2. Mac-Specific Optimizations
- **MacRoman Encoding**: Added support for Mac-specific encoding
- **UTF-8 Configuration**: Forces UTF-8 mode in Mac environments
- **Locale Settings**: Applies Mac-friendly locale settings (LC_ALL, LANG)

### 3. File Upload Improvements
- **Filename Sanitization**: Removes special characters that might cause issues
- **Path Normalization**: Uses cross-platform path handling
- **Enhanced Error Handling**: Better error messages for upload failures

## How to Test on Mac

### Option 1: Use the Diagnostic Tool
```bash
python mac_csv_test.py your_csv_file.csv
```

This will:
- Detect your file's encoding
- Test multiple encoding options
- Simulate the full upload process
- Provide specific recommendations

### Option 2: Manual Testing
1. Run the application: `python local_run.py`
2. Try uploading your CSV file
3. Check the console output for encoding information

## Common Mac CSV Issues and Solutions

### Issue: "UnicodeDecodeError"
**Solution**: The file encoding is not standard UTF-8
- Export from Excel as "CSV UTF-8 (Comma delimited)"
- Or use the diagnostic tool to find compatible encoding

### Issue: "File upload failed - file is empty"
**Solution**: File permissions or path issues
- Check file permissions: `ls -la your_file.csv`
- Ensure file is not locked or in use by another app

### Issue: "Could not read CSV file with any supported encoding"
**Solution**: File format issues
- Ensure it's a proper comma-separated CSV
- Check for special characters in the file
- Try saving with different CSV export options

## Supported CSV Formats on Mac

✅ **Works Well:**
- Excel → "CSV UTF-8 (Comma delimited)" 
- Numbers → Export as CSV
- UTF-8 encoded files from any text editor

⚠️ **May Need Conversion:**
- Excel → "CSV (Comma delimited)" (uses Windows encoding)
- CSV files created on Windows systems
- Files with special characters

## Quick Fix Commands

```bash
# Convert problematic CSV to UTF-8 (if you have iconv)
iconv -f iso-8859-1 -t utf-8 input.csv > output.csv

# Check file encoding
file -I your_file.csv

# Make diagnostic tool executable
chmod +x mac_csv_test.py
```

## Environment Variables for Mac

The application now automatically sets these for Mac users:
- `LC_ALL=en_US.UTF-8`
- `LANG=en_US.UTF-8` 
- `PYTHONIOENCODING=utf-8`

## Contact Support

If you're still experiencing issues:
1. Run the diagnostic tool and save the output
2. Note your Mac OS version and Python version
3. Include the specific error message
4. Provide a sample of your CSV file (first few rows)