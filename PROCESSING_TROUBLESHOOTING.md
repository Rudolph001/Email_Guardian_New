# Email Guardian Processing Troubleshooting Guide

## Quick Fixes for Processing Issues

If your Email Guardian is getting stuck during processing, here are the solutions:

### 1. 🚀 Instant Speed Boost (Recommended)

Run the speed optimization script:
```bash
python optimize_for_speed.py
```

This enables fast mode and can make processing **60-80% faster**.

### 2. 🔍 Check Processing Status

Use the debug tool to see what's happening:
```bash
python processing_debug.py
```

Select option "1" to check all session statuses. This shows you:
- Which sessions are stuck
- How many records were processed
- Which processing steps completed

### 3. 🔧 Fix Stuck Sessions

If you have sessions stuck in "processing" state:
```bash
python processing_debug.py
```

Select option "2" to automatically fix stuck sessions. This will:
- Mark completed sessions as "completed"
- Mark failed sessions as "error"
- Allow you to retry processing

### 4. 🚿 Simple Processing Mode

For very large files or if normal processing fails:
```python
from simple_processor import run_simple_processing

# Replace with your actual session ID and file path
run_simple_processing("your-session-id", "path/to/your/file.csv")
```

Simple mode:
- Processes files much faster
- Skips complex ML analysis
- Still provides basic threat detection
- Perfect for initial data exploration

### 5. 📊 Performance Settings

Add these to your environment for maximum speed:

```bash
# Ultra-fast mode settings
export EMAIL_GUARDIAN_FAST_MODE=true
export EMAIL_GUARDIAN_CHUNK_SIZE=2000
export EMAIL_GUARDIAN_MAX_ML_RECORDS=1000
export EMAIL_GUARDIAN_ML_ESTIMATORS=25
export EMAIL_GUARDIAN_PROGRESS_INTERVAL=1000
```

### 6. 🔄 Reset Session

To completely reset a session for reprocessing:
```bash
python processing_debug.py
```

Select option "4" and enter your session ID. This clears all processing results and lets you start fresh.

## Common Issues and Solutions

### Issue: "Processing stuck at 0 records"
**Solution**: The file might have column name mismatches. Check that your CSV has these columns:
- `_time`, `sender`, `subject`, `recipients`, `recipients_email_domain`

### Issue: "Processing takes forever"
**Solution**: 
1. Run `python optimize_for_speed.py`
2. Use simple processing mode for initial analysis
3. For very large files (>10,000 records), fast mode is essential

### Issue: "Session shows as processing but nothing happens"
**Solution**:
1. Run `python processing_debug.py`
2. Select option "2" to fix stuck sessions
3. Try reprocessing with fast mode enabled

### Issue: "Error during ML analysis"
**Solution**:
1. Enable fast mode to limit ML analysis scope
2. Use simple processing mode as alternative
3. Check if file has enough valid records (need at least 3)

## Performance Expectations

| File Size | Standard Mode | Fast Mode | Simple Mode |
|-----------|---------------|-----------|-------------|
| < 1,000 records | 1-2 min | 30-60 sec | 15-30 sec |
| 1,000-5,000 | 3-8 min | 1-3 min | 30-90 sec |
| 5,000-10,000 | 8-15 min | 3-6 min | 1-2 min |
| > 10,000 | 15+ min | 6-10 min | 2-4 min |

## Getting Help

If you're still having issues:

1. **Check the logs**: Look for any error messages in the console
2. **Run the debug tool**: Use `python processing_debug.py` to get detailed status
3. **Try simple mode**: Use simple processing for quick results
4. **Enable fast mode**: Use performance optimizations for large files

The system is now optimized and should handle most CSV files efficiently!