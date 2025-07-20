#!/usr/bin/env python3
"""
Test script to verify the local whitelist functionality works
"""

import os
import sys
import sqlite3

def test_whitelist_setup():
    """Test that the whitelist functionality is properly set up in local version"""
    print("Testing Email Guardian local whitelist setup...")
    print()
    
    # Check if local database exists
    db_path = 'local_email_guardian.db'
    if os.path.exists(db_path):
        print("✓ Local database file exists")
        
        # Check database structure
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if whitelist_domains table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='whitelist_domains';")
            table_exists = cursor.fetchone()
            
            if table_exists:
                print("✓ Whitelist domains table exists")
                
                # Check if default domains exist
                cursor.execute("SELECT COUNT(*) FROM whitelist_domains;")
                count = cursor.fetchone()[0]
                print(f"✓ Found {count} whitelist domains in database")
                
                if count > 0:
                    cursor.execute("SELECT domain, domain_type FROM whitelist_domains ORDER BY added_at;")
                    domains = cursor.fetchall()
                    print("\nDefault whitelist domains:")
                    for domain, domain_type in domains:
                        print(f"  • {domain} ({domain_type})")
                else:
                    print("⚠ No whitelist domains found - they will be created when the app starts")
            else:
                print("⚠ Whitelist domains table doesn't exist - it will be created when the app starts")
            
            conn.close()
            
        except sqlite3.Error as e:
            print(f"✗ Database error: {e}")
    else:
        print("⚠ Local database doesn't exist yet - it will be created when the app starts")
    
    print()
    
    # Check if local_standalone.py has the required routes
    print("Checking local_standalone.py for whitelist routes...")
    
    try:
        with open('local_standalone.py', 'r') as f:
            content = f.read()
            
        routes_to_check = [
            "whitelist-domains",
            "api/whitelist-domains", 
            "WhitelistDomain",
            "jsonify"
        ]
        
        missing_routes = []
        for route in routes_to_check:
            if route in content:
                print(f"✓ Found {route}")
            else:
                missing_routes.append(route)
                print(f"✗ Missing {route}")
        
        if not missing_routes:
            print("\n✅ All whitelist functionality appears to be properly implemented!")
            print("\nTo fix the 'whitelist_domains' error:")
            print("1. Stop the current local application (Ctrl+C)")
            print("2. Run: python local_standalone.py")
            print("3. Navigate to: http://127.0.0.1:5000/whitelist-domains")
        else:
            print(f"\n❌ Missing required components: {missing_routes}")
            print("The whitelist functionality needs to be completed")
            
    except FileNotFoundError:
        print("✗ local_standalone.py not found")
    
    print()
    print("Testing complete!")

if __name__ == '__main__':
    test_whitelist_setup()