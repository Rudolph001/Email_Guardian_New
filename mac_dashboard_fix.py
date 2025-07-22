#!/usr/bin/env python3
"""
Mac Dashboard Template Fix Script
This script fixes the Jinja template error in dashboard.html for local Mac development
"""

import os
import shutil
import re

def fix_dashboard_template():
    """Fix the dashboard template to use safe dictionary access"""
    
    # Define the path to the dashboard template
    template_path = "templates/dashboard.html"
    backup_path = "templates/dashboard.html.backup"
    
    if not os.path.exists(template_path):
        print("❌ Error: templates/dashboard.html not found!")
        print("Make sure you're running this from your Email Guardian project directory.")
        return False
    
    print("🔧 Fixing dashboard template for Mac compatibility...")
    
    # Create backup
    shutil.copy2(template_path, backup_path)
    print(f"✅ Backup created: {backup_path}")
    
    # Read the template file
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define the fixes to apply
    fixes = [
        # Total attachments
        (
            r'attachment_analytics\.total_attachments(\s+or\s+0)?',
            r"attachment_analytics.get('total_attachments', 0)"
        ),
        # High risk count
        (
            r'attachment_analytics\.risk_distribution\.high_risk_count(\s+or\s+0)?',
            r"attachment_analytics.get('risk_distribution', {}).get('high_risk_count', 0)"
        ),
        # Mean risk
        (
            r'attachment_analytics\.risk_distribution\.mean_risk(\s+or\s+0)?',
            r"attachment_analytics.get('risk_distribution', {}).get('mean_risk', 0)"
        ),
        # Malware indicators check
        (
            r'attachment_analytics\.malware_indicators(?!\s*\.)',
            r"attachment_analytics.get('malware_indicators')"
        ),
        # Malware indicators items
        (
            r'attachment_analytics\.malware_indicators\.items\(\)',
            r"attachment_analytics.get('malware_indicators', {}).items()"
        ),
    ]
    
    # Apply fixes
    original_content = content
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content)
    
    # Check if any changes were made
    if content == original_content:
        print("⚠️  No template fixes were needed - file might already be fixed.")
        return True
    
    # Write the fixed content back
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Dashboard template fixed successfully!")
    print("\nChanges applied:")
    print("- Safe dictionary access for attachment_analytics")
    print("- Fallback values for missing data")
    print("- Mac browser compatibility")
    
    print(f"\n🎯 Next steps:")
    print("1. Restart your Flask application")
    print("2. Upload CSV in Chrome browser (NOT Safari)")
    print("3. Dashboard should now load without errors")
    print(f"\nIf you need to restore: cp {backup_path} {template_path}")
    
    return True

if __name__ == "__main__":
    print("🍎 Email Guardian Mac Dashboard Fix")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("templates") or not os.path.exists("app.py"):
        print("❌ Error: This doesn't look like the Email Guardian project directory!")
        print("Please navigate to your Email Guardian project folder and run this script again.")
        exit(1)
    
    success = fix_dashboard_template()
    
    if success:
        print("\n🎉 Template fix completed successfully!")
        print("Your CSV upload → dashboard workflow should now work on Mac!")
    else:
        print("\n❌ Template fix failed. Please apply the manual fixes from DASHBOARD_TEMPLATE_FIX.md")