#!/usr/bin/env python3
"""
Sync Manager for Email Guardian
Handles version updates and data synchronization for multi-user deployments
"""

import os
import sys
import json
import shutil
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SyncManager:
    """Manages code updates and data synchronization"""
    
    def __init__(self):
        self.project_dir = Path.cwd()
        self.data_backup_dir = self.project_dir / "data_backup"
        self.config_file = self.project_dir / "sync_config.json"
        self.version_file = self.project_dir / "version.json"
        
    def get_current_version(self):
        """Get current application version"""
        if self.version_file.exists():
            with open(self.version_file, 'r') as f:
                return json.load(f).get('version', '1.0.0')
        return '1.0.0'
    
    def set_version(self, version):
        """Set application version"""
        version_data = {
            'version': version,
            'updated_at': datetime.now().isoformat(),
            'updated_by': os.getenv('USER', 'system')
        }
        with open(self.version_file, 'w') as f:
            json.dump(version_data, f, indent=2)
    
    def backup_user_data(self):
        """Backup user uploads, data, and database"""
        print("Backing up user data...")
        
        # Create backup directory with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.data_backup_dir / f"backup_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup directories
        directories_to_backup = ['uploads', 'data', 'instance']
        
        for dir_name in directories_to_backup:
            source_dir = self.project_dir / dir_name
            if source_dir.exists():
                dest_dir = backup_dir / dir_name
                shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)
                print(f"✓ Backed up {dir_name}/")
        
        # Backup whitelist domains to JSON (portable format)
        self.export_whitelist_domains(backup_dir / "whitelist_export.json")
        
        print(f"✓ Backup completed: {backup_dir}")
        return backup_dir
    
    def restore_user_data(self, backup_dir=None):
        """Restore user data from backup"""
        if backup_dir is None:
            # Find most recent backup
            if not self.data_backup_dir.exists():
                print("No backups found")
                return False
            
            backups = list(self.data_backup_dir.glob("backup_*"))
            if not backups:
                print("No backups found")
                return False
            
            backup_dir = max(backups, key=lambda p: p.stat().st_mtime)
        
        print(f"Restoring user data from {backup_dir}...")
        
        # Restore directories
        directories_to_restore = ['uploads', 'data', 'instance']
        
        for dir_name in directories_to_restore:
            source_dir = backup_dir / dir_name
            dest_dir = self.project_dir / dir_name
            
            if source_dir.exists():
                if dest_dir.exists():
                    shutil.rmtree(dest_dir)
                shutil.copytree(source_dir, dest_dir)
                print(f"✓ Restored {dir_name}/")
        
        # Import whitelist domains if available
        whitelist_file = backup_dir / "whitelist_export.json"
        if whitelist_file.exists():
            self.import_whitelist_domains(whitelist_file)
        
        print("✓ User data restored")
        return True
    
    def export_whitelist_domains(self, export_file):
        """Export whitelist domains to JSON file"""
        try:
            # Set up environment for database access
            os.environ.setdefault('SESSION_SECRET', 'dev-secret-change-in-production')
            db_path = Path('instance/email_guardian.db').absolute()
            os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
            
            from app import app, db
            from models import WhitelistDomain
            
            with app.app_context():
                domains = WhitelistDomain.query.filter_by(is_active=True).all()
                domain_data = []
                
                for domain in domains:
                    domain_data.append({
                        'domain': domain.domain,
                        'domain_type': domain.domain_type,
                        'added_by': domain.added_by,
                        'added_at': domain.added_at.isoformat() if domain.added_at else None,
                        'notes': domain.notes
                    })
                
                with open(export_file, 'w') as f:
                    json.dump(domain_data, f, indent=2)
                
                print(f"✓ Exported {len(domain_data)} whitelist domains")
                
        except Exception as e:
            print(f"Warning: Could not export whitelist domains: {e}")
    
    def import_whitelist_domains(self, import_file):
        """Import whitelist domains from JSON file"""
        try:
            # Set up environment for database access
            os.environ.setdefault('SESSION_SECRET', 'dev-secret-change-in-production')
            db_path = Path('instance/email_guardian.db').absolute()
            os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
            
            from app import app, db
            from models import WhitelistDomain
            
            with open(import_file, 'r') as f:
                domain_data = json.load(f)
            
            with app.app_context():
                imported_count = 0
                
                for domain_info in domain_data:
                    # Check if domain already exists
                    existing = WhitelistDomain.query.filter_by(domain=domain_info['domain']).first()
                    
                    if not existing:
                        new_domain = WhitelistDomain(
                            domain=domain_info['domain'],
                            domain_type=domain_info.get('domain_type'),
                            added_by=domain_info.get('added_by'),
                            notes=domain_info.get('notes'),
                            is_active=True
                        )
                        
                        if domain_info.get('added_at'):
                            try:
                                new_domain.added_at = datetime.fromisoformat(domain_info['added_at'])
                            except:
                                pass
                        
                        db.session.add(new_domain)
                        imported_count += 1
                
                db.session.commit()
                print(f"✓ Imported {imported_count} new whitelist domains")
                
        except Exception as e:
            print(f"Warning: Could not import whitelist domains: {e}")
    
    def pull_updates(self):
        """Pull latest code from Git repository"""
        print("Pulling latest updates from Git...")
        
        try:
            # Check if we're in a git repository
            result = subprocess.run(['git', 'status'], 
                                  capture_output=True, text=True, cwd=self.project_dir)
            
            if result.returncode != 0:
                print("✗ Not a Git repository. Initialize with: git init")
                return False
            
            # Stash any local changes
            subprocess.run(['git', 'stash'], cwd=self.project_dir)
            
            # Pull latest changes
            result = subprocess.run(['git', 'pull'], 
                                  capture_output=True, text=True, cwd=self.project_dir)
            
            if result.returncode == 0:
                print("✓ Successfully pulled latest updates")
                return True
            else:
                print(f"✗ Failed to pull updates: {result.stderr}")
                return False
                
        except FileNotFoundError:
            print("✗ Git not found. Please install Git.")
            return False
        except Exception as e:
            print(f"✗ Error pulling updates: {e}")
            return False
    
    def push_whitelist_updates(self):
        """Push whitelist changes to repository (if configured)"""
        # Export current whitelist to a shareable format
        shared_whitelist_file = self.project_dir / "shared_whitelist.json"
        self.export_whitelist_domains(shared_whitelist_file)
        
        try:
            # Add the shared whitelist file to git
            subprocess.run(['git', 'add', 'shared_whitelist.json'], cwd=self.project_dir)
            
            # Commit the changes
            commit_message = f"Update shared whitelist - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            result = subprocess.run(['git', 'commit', '-m', commit_message], 
                                  capture_output=True, text=True, cwd=self.project_dir)
            
            if result.returncode == 0:
                # Push to remote
                push_result = subprocess.run(['git', 'push'], 
                                           capture_output=True, text=True, cwd=self.project_dir)
                
                if push_result.returncode == 0:
                    print("✓ Whitelist updates pushed to repository")
                    return True
                else:
                    print(f"✗ Failed to push: {push_result.stderr}")
                    return False
            else:
                print("No whitelist changes to commit")
                return True
                
        except Exception as e:
            print(f"Warning: Could not push whitelist updates: {e}")
            return False
    
    def update_application(self):
        """Complete application update process"""
        print("=== Email Guardian Update Process ===")
        print()
        
        current_version = self.get_current_version()
        print(f"Current version: {current_version}")
        
        # Step 1: Backup user data
        backup_dir = self.backup_user_data()
        
        # Step 2: Pull latest code
        if self.pull_updates():
            # Step 3: Run database migration
            print("Running database migration...")
            try:
                subprocess.run([sys.executable, 'migrate_local_db.py'], 
                             cwd=self.project_dir, check=True)
                print("✓ Database migration completed")
            except subprocess.CalledProcessError as e:
                print(f"✗ Database migration failed: {e}")
                print("Restoring from backup...")
                self.restore_user_data(backup_dir)
                return False
            
            # Step 4: Restore user data
            self.restore_user_data(backup_dir)
            
            # Step 5: Import shared whitelist if available
            shared_whitelist = self.project_dir / "shared_whitelist.json"
            if shared_whitelist.exists():
                print("Importing shared whitelist...")
                self.import_whitelist_domains(shared_whitelist)
            
            print("✓ Application update completed successfully!")
            return True
        else:
            print("✗ Update failed")
            return False

def main():
    """Main sync manager CLI"""
    if len(sys.argv) < 2:
        print("""
Email Guardian Sync Manager

Usage:
    python sync_manager.py update     - Update application from Git
    python sync_manager.py backup     - Backup user data
    python sync_manager.py restore    - Restore latest backup
    python sync_manager.py push       - Push whitelist changes to Git
    python sync_manager.py version    - Show current version
        """)
        return
    
    sync_manager = SyncManager()
    command = sys.argv[1].lower()
    
    if command == 'update':
        sync_manager.update_application()
    elif command == 'backup':
        sync_manager.backup_user_data()
    elif command == 'restore':
        sync_manager.restore_user_data()
    elif command == 'push':
        sync_manager.push_whitelist_updates()
    elif command == 'version':
        print(f"Current version: {sync_manager.get_current_version()}")
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()