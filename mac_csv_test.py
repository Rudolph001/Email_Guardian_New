#!/usr/bin/env python3
"""
Mac-specific CSV upload test and diagnostics for Email Guardian
This tool helps identify and fix CSV upload issues on Mac systems
"""

import os
import sys
import pandas as pd
import chardet
from pathlib import Path

def detect_csv_encoding(file_path):
    """Detect CSV file encoding"""
    print(f"Testing file: {file_path}")
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return None
    
    print(f"✓ File exists: {os.path.getsize(file_path)} bytes")
    
    # Detect encoding
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)  # Read first 10KB
        
        result = chardet.detect(raw_data)
        encoding = result.get('encoding', 'unknown')
        confidence = result.get('confidence', 0)
        
        print(f"✓ Detected encoding: {encoding} (confidence: {confidence:.2f})")
        return encoding
    except Exception as e:
        print(f"❌ Encoding detection failed: {str(e)}")
        return None

def test_csv_reading(file_path):
    """Test reading CSV with different encodings"""
    print("\n=== Testing CSV Reading ===")
    
    # List of encodings to try (Mac-specific ones included)
    encodings = ['utf-8', 'utf-8-sig', 'iso-8859-1', 'cp1252', 'macroman', 'utf-16']
    
    # Detect encoding first
    detected_encoding = detect_csv_encoding(file_path)
    if detected_encoding and detected_encoding not in encodings:
        encodings.insert(0, detected_encoding)
    
    successful_encodings = []
    
    for encoding in encodings:
        try:
            print(f"Testing encoding: {encoding}")
            df = pd.read_csv(file_path, nrows=5, encoding=encoding)
            print(f"✓ Success with {encoding}: {len(df.columns)} columns, {len(df)} rows")
            print(f"  Columns: {list(df.columns)[:5]}...")  # Show first 5 columns
            successful_encodings.append(encoding)
            
            # Test a larger chunk
            df_large = pd.read_csv(file_path, nrows=100, encoding=encoding)
            print(f"  Large test: {len(df_large)} rows processed successfully")
            
        except UnicodeDecodeError as e:
            print(f"❌ Unicode error with {encoding}: {str(e)[:100]}...")
        except Exception as e:
            print(f"❌ Error with {encoding}: {str(e)[:100]}...")
    
    return successful_encodings

def check_system_info():
    """Check Mac system information"""
    print("\n=== System Information ===")
    print(f"Platform: {sys.platform}")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"pandas version: {pd.__version__}")
    
    # Check locale settings
    try:
        import locale
        print(f"System locale: {locale.getdefaultlocale()}")
        print(f"Preferred encoding: {locale.getpreferredencoding()}")
    except:
        pass

def test_file_upload(csv_file):
    """Simulate the upload process"""
    print("\n=== Simulating Upload Process ===")
    
    if not csv_file or not os.path.exists(csv_file):
        print("❌ No CSV file provided or file doesn't exist")
        return False
    
    try:
        # Test encoding detection
        encoding = detect_csv_encoding(csv_file)
        if not encoding:
            print("❌ Could not detect encoding")
            return False
        
        # Test CSV structure validation
        print("Testing CSV structure validation...")
        df = pd.read_csv(csv_file, nrows=5, encoding=encoding)
        print(f"✓ CSV structure validation passed: {len(df.columns)} columns")
        
        # Test chunked reading (simulates actual processing)
        print("Testing chunked reading...")
        chunk_count = 0
        for chunk in pd.read_csv(csv_file, chunksize=1000, encoding=encoding):
            chunk_count += 1
            if chunk_count >= 3:  # Test first 3 chunks
                break
        print(f"✓ Chunked reading successful: {chunk_count} chunks tested")
        
        return True
        
    except Exception as e:
        print(f"❌ Upload simulation failed: {str(e)}")
        return False

def main():
    """Main diagnostic function"""
    print("=== Email Guardian Mac CSV Diagnostic Tool ===")
    
    # Check system info
    check_system_info()
    
    # Get CSV file from command line or prompt
    csv_file = None
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        csv_file = input("\nEnter path to CSV file to test (or press Enter to skip): ").strip()
    
    if csv_file and csv_file != "":
        # Test the specific file
        successful_encodings = test_csv_reading(csv_file)
        
        if successful_encodings:
            print(f"\n✅ SUCCESS: File can be read with encodings: {successful_encodings}")
            print(f"Recommended encoding: {successful_encodings[0]}")
            
            # Test full upload simulation
            if test_file_upload(csv_file):
                print("\n🎉 UPLOAD SIMULATION SUCCESSFUL!")
                print("Your CSV file should work with Email Guardian on Mac.")
            else:
                print("\n❌ Upload simulation failed. Check the errors above.")
        else:
            print("\n❌ FAILED: Could not read CSV file with any encoding")
            print("Possible solutions:")
            print("1. Save the CSV file with UTF-8 encoding")
            print("2. Use Excel to export as CSV (UTF-8)")
            print("3. Convert the file using: iconv -f <from_encoding> -t utf-8 input.csv > output.csv")
    
    else:
        print("\nNo CSV file provided. Skipping file tests.")
    
    print("\n=== Diagnostic Complete ===")
    print("If you're still having issues:")
    print("1. Check that the CSV file uses standard comma separators")
    print("2. Ensure the file is saved with UTF-8 encoding")
    print("3. Try exporting from Excel as 'CSV UTF-8 (Comma delimited)'")
    print("4. Contact support with the output above")

if __name__ == "__main__":
    main()