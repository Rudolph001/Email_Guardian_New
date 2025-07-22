# Email Guardian - Multi-User Local Deployment Guide

## Overview

This guide explains how to deploy Email Guardian for multiple users while maintaining version control and preserving user data.

## Initial Setup

### 1. Clone Repository
```bash
git clone <your-repository-url>
cd Email_Guardian
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize Database
```bash
python3 migrate_local_db.py
```

### 4. Start Application
```bash
python3 local_run.py
```

## Multi-User Workflow

### For Developers (Making Changes)

1. **Make your changes** to the codebase
2. **Test locally** to ensure everything works
3. **Update version** (optional):
   ```bash
   python3 sync_manager.py version
   ```
4. **Commit and push** changes:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin main
   ```

### For Users (Getting Updates)

1. **Update application** with preserved data:
   ```bash
   python3 sync_manager.py update
   ```

This command will:
- Backup your uploads, data, and database
- Pull latest code from Git
- Run database migrations
- Restore your data
- Import any shared whitelists

### Sharing Whitelists Between Users

**To share your whitelist additions:**
```bash
python3 sync_manager.py push
```

**To get whitelist updates from others:**
```bash
python3 sync_manager.py update
```

## Data Management

### What Gets Preserved
- ✅ **Uploaded CSV files** (`uploads/` directory)
- ✅ **Analysis data** (`data/` directory) 
- ✅ **Database** (processing sessions, cases, etc.)
- ✅ **Whitelist domains** (exported/imported automatically)
- ✅ **Custom rules** (stored in database)

### What Gets Updated
- ✅ **Application code** (Python files, templates, etc.)
- ✅ **Database schema** (automatic migrations)
- ✅ **Dependencies** (requirements.txt)
- ✅ **Shared whitelist** (merged with your local list)

### Manual Backup/Restore

**Create backup:**
```bash
python3 sync_manager.py backup
```

**Restore from backup:**
```bash
python3 sync_manager.py restore
```

## Git Configuration

### .gitignore Setup
The `.gitignore` file is configured to exclude:
- User uploads (`uploads/`)
- Analysis data (`data/`)
- Databases (`instance/`, `*.db`)
- Environment files (`.env`)

### Repository Structure
```
Email_Guardian/
├── .gitignore              # Excludes user data
├── sync_manager.py         # Update and sync tool
├── migrate_local_db.py     # Database migration
├── shared_whitelist.json   # Shared whitelist (tracked)
├── version.json           # Version tracking
├── app.py                 # Application code (tracked)
├── routes.py              # Routes (tracked)
├── models.py              # Database models (tracked)
├── requirements.txt       # Dependencies (tracked)
├── uploads/               # User files (ignored)
├── data/                  # Analysis data (ignored)
└── instance/              # Database (ignored)
```

## Troubleshooting

### Update Failed
If an update fails, your data is automatically restored from backup:
```bash
python3 sync_manager.py restore
```

### Database Issues
Run migration manually:
```bash
python3 migrate_local_db.py
```

### Conflict Resolution
If you have local changes that conflict with updates:
```bash
git stash                    # Save local changes
python3 sync_manager.py update
git stash pop               # Restore local changes
```

## Version Control Best Practices

### For Development Team
1. **Use feature branches** for major changes
2. **Test thoroughly** before merging to main
3. **Update version.json** for significant releases
4. **Document changes** in commit messages

### For Users
1. **Regular updates** to get latest features and fixes
2. **Backup before updates** (done automatically)
3. **Share whitelist changes** with the team
4. **Report issues** through your preferred channel

## Security Considerations

- **Local deployment only** - no external access
- **User data stays local** - never committed to Git
- **Whitelist sharing** - only domain names, no sensitive data
- **Environment files** - keep `.env` files local and secure

## Advanced Usage

### Custom Update Schedule
Set up automatic updates with cron (Linux/Mac):
```bash
# Add to crontab: daily updates at 2 AM
0 2 * * * cd /path/to/Email_Guardian && python3 sync_manager.py update
```

### Team Whitelist Management
1. Designate a whitelist manager
2. Regular whitelist review meetings
3. Shared whitelist updates via Git
4. Document whitelist decisions

### Multiple Environments
For development, staging, and production:
```bash
# Use different branches
git checkout development
python3 sync_manager.py update

git checkout staging  
python3 sync_manager.py update
```

## Support

For issues with:
- **Application bugs**: Check Git issues or contact development team
- **Update problems**: Run `python3 sync_manager.py restore`
- **Data loss**: Backups are in `data_backup/` directory
- **Database issues**: Run `python3 migrate_local_db.py`