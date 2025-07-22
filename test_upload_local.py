#!/usr/bin/env python3
"""
Test script for local CSV upload functionality
Creates a sample CSV file and tests the upload process
"""

import os
import sys
import csv
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def create_test_csv():
    """Create a test CSV file with sample Tessian export data"""
    test_data = [
        {
            '_time': '2024-01-15 09:30:00',
            'sender': 'test.user@company.com',
            'subject': 'Quarterly Report',
            'attachments': 'report.xlsx',
            'recipients': 'external@partner.com',
            'recipients_email_domain': 'partner.com',
            'leaver': 'false',
            'termination_date': '',
            'wordlist_attachment': 'quarterly,financial',
            'wordlist_subject': 'report,quarterly',
            'bunit': 'Finance',
            'department': 'Accounting',
            'status': 'sent',
            'user_response': 'approved',
            'final_outcome': 'allowed',
            'justification': 'Regular quarterly report to approved partner'
        },
        {
            '_time': '2024-01-15 14:22:00',
            'sender': 'admin@company.com',
            'subject': 'Confidential: Employee Data',
            'attachments': 'employee_list.csv',
            'recipients': 'unknown@external.com',
            'recipients_email_domain': 'external.com',
            'leaver': 'true',
            'termination_date': '2024-01-10',
            'wordlist_attachment': 'employee,confidential,personal',
            'wordlist_subject': 'confidential,employee',
            'bunit': 'HR',
            'department': 'Human Resources',
            'status': 'blocked',
            'user_response': 'blocked',
            'final_outcome': 'blocked',
            'justification': 'Leaver attempting to send confidential data'
        },
        {
            '_time': '2024-01-15 16:45:00',
            'sender': 'sales@company.com',
            'subject': 'Customer Contact List',
            'attachments': 'contacts.xlsx',
            'recipients': 'competitor@rival.com',
            'recipients_email_domain': 'rival.com',
            'leaver': 'false',
            'termination_date': '',
            'wordlist_attachment': 'customer,contact,phone,email',
            'wordlist_subject': 'customer,contact',
            'bunit': 'Sales',
            'department': 'Business Development',
            'status': 'flagged',
            'user_response': 'pending',
            'final_outcome': 'under_review',
            'justification': 'Suspicious recipient - competitor domain'
        }
    ]
    
    # Create uploads directory if it doesn't exist
    Path('uploads').mkdir(exist_ok=True)
    
    # Write test CSV
    test_file = 'uploads/test_email_export.csv'
    with open(test_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = test_data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in test_data:
            writer.writerow(row)
    
    print(f"✓ Created test CSV file: {test_file}")
    print(f"  - Records: {len(test_data)}")
    print(f"  - Columns: {len(fieldnames)}")
    print(f"  - File size: {Path(test_file).stat().st_size} bytes")
    return test_file

def test_local_environment():
    """Test the local environment setup"""
    print("=== Testing Local Environment ===")
    
    # Set up environment variables
    os.environ['DATABASE_URL'] = f'sqlite:///{Path("instance/email_guardian.db").absolute()}'
    os.environ['SESSION_SECRET'] = 'IbV9R1thLbcFKB9-UR4sHOe1ePE-zUamWbypp3ava7o'
    os.environ['FLASK_ENV'] = 'development'
    
    # Create directories
    for directory in ['uploads', 'data', 'instance']:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Directory created: {directory}/")
    
    try:
        # Test import
        from app import app, db
        print("✓ Flask app imported successfully")
        
        # Test database connection
        with app.app_context():
            db.create_all()
            print("✓ Database tables created/verified")
            
            # Test basic query
            from models import ProcessingSession
            count = ProcessingSession.query.count()
            print(f"✓ Database connection successful ({count} sessions found)")
            
    except Exception as e:
        print(f"✗ Error testing environment: {e}")
        return False
    
    return True

def main():
    """Main test function"""
    print("=== Email Guardian Local Upload Test ===\n")
    
    # Test environment
    if not test_local_environment():
        print("Environment test failed. Check the error messages above.")
        return False
    
    # Create test file
    test_file = create_test_csv()
    
    print("\n=== Next Steps ===")
    print("1. Run: python local_run.py")
    print("2. Open: http://localhost:5000")
    print(f"3. Upload the test file: {test_file}")
    print("\nThe test CSV contains 3 sample records with different risk levels.")
    print("This should help identify any upload issues in your local environment.")
    
    return True

if __name__ == "__main__":
    main()