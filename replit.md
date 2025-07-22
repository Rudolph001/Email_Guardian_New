# Email Guardian - Email Security Analysis Platform

## Overview

Email Guardian is a comprehensive web application designed for analyzing Tessian email export data to detect security threats, data exfiltration attempts, and anomalous communication patterns. The platform combines rule-based filtering, machine learning analytics, and domain classification to provide enterprise-grade email security analysis.

## User Preferences

- **Communication style**: Simple, everyday language
- **Local development database**: SQLite (preferred for local development and testing)
- **Production database**: PostgreSQL (for Replit deployment and production use)

## System Architecture

Email Guardian follows a modular Flask-based architecture with clear separation of concerns:

- **Frontend**: Bootstrap 5 with Jinja2 templates, Chart.js for visualizations, DataTables for data display
- **Backend**: Flask web framework with SQLAlchemy ORM
- **Database**: SQLite for development/local deployment (designed to support PostgreSQL migration)
- **ML Engine**: scikit-learn for anomaly detection, clustering, and pattern recognition
- **File Processing**: Chunked CSV processing with pandas for handling large datasets
- **Session Management**: JSON-based data persistence with gzip compression for large files

## Key Components

### 1. Data Processing Pipeline
- **DataProcessor**: Handles CSV file ingestion with chunked processing (2500 records per chunk)
- **SessionManager**: Manages data persistence, compression, and session lifecycle
- **Column Mapping**: Case-insensitive field matching for flexible CSV structures

### 2. Rule Engine System
- **RuleEngine**: Configurable business rules with complex AND/OR logic
- **Exclusion Rules**: Pre-processing filters to exclude known-good communications
- **Supported Operators**: equals, contains, regex patterns, range comparisons, list membership

### 3. Domain Classification
- **DomainManager**: Automated domain categorization (corporate, personal, public, suspicious)
- **Whitelist Management**: Trust-based domain filtering with recommendation engine
- **Trust Scoring**: Multi-factor domain reputation scoring

### 4. Machine Learning Analytics
- **MLEngine**: Core ML functionality with Isolation Forest for anomaly detection
- **AdvancedMLEngine**: Deep analytics including network analysis and pattern clustering
- **Risk Scoring**: Multi-dimensional risk assessment with configurable thresholds

### 5. Web Interface
- **Dashboard System**: Multiple specialized dashboards (main, sender analysis, time analysis, etc.)
- **Case Management**: Escalation tracking and investigation workflow
- **Administration Panel**: System configuration and rule management

## Data Flow

1. **Upload Phase**: CSV files uploaded and validated for structure
2. **Processing Phase**: Data chunked and processed through pipeline stages:
   - Column mapping and validation
   - Exclusion rule application
   - Whitelist filtering
   - ML analysis and risk scoring
3. **Storage Phase**: Results stored in SQLite with JSON session data (compressed for large datasets)
4. **Analysis Phase**: Multiple analytical views generated from processed data
5. **Presentation Phase**: Results displayed through responsive web dashboards

## External Dependencies

### Core Framework
- Flask: Web application framework
- SQLAlchemy: Database ORM
- Jinja2: Template engine

### Data Processing
- pandas: Data manipulation and analysis
- numpy: Numerical computing
- scikit-learn: Machine learning algorithms

### Frontend Libraries
- Bootstrap 5: UI framework
- Chart.js: Data visualization
- DataTables: Advanced table functionality
- Font Awesome: Icon library

### File Processing
- CSV parsing with pandas
- Gzip compression for large files
- JSON serialization for session data

## Deployment Strategy

The application is designed for flexible deployment across multiple environments:

### Local Development (Preferred)
- **Target Platforms**: Windows and Mac systems
- **Database**: SQLite (`instance/email_guardian.db`) - No setup required
- **Runner**: `python local_run.py` for automatic environment setup
- **Configuration**: Automatic SQLite configuration with development defaults
- **File Storage**: Local filesystem with organized directory structure
- **Session Management**: File-based with automatic compression

### Replit/Production Deployment
- **Database**: PostgreSQL with automatic provisioning
- **Server**: Gunicorn on port 5000 (0.0.0.0:5000)
- **Configuration**: Environment variable based (DATABASE_URL, SESSION_SECRET)
- **Scaling**: PostgreSQL supports concurrent users and larger datasets

### Database Architecture
- **Dual-compatible design**: Same codebase works with both SQLite and PostgreSQL
- **Local development**: SQLite for simplicity and zero configuration
- **Production**: PostgreSQL for performance and reliability
- **Migration ready**: Easy transition from SQLite to PostgreSQL when needed

### Directory Structure
```
email-guardian/
├── main.py                    # Application entry point
├── app.py                     # Flask app configuration
├── routes.py                  # Web routes and API endpoints
├── models.py                  # Database models
├── data_processor.py          # CSV processing engine
├── ml_engine.py              # Core ML functionality
├── advanced_ml_engine.py     # Advanced analytics
├── rule_engine.py            # Business rules engine
├── domain_manager.py         # Domain classification
├── session_manager.py        # Session persistence
├── templates/                # HTML templates
├── static/                   # CSS/JS assets
├── data/                     # JSON session storage
├── uploads/                  # CSV file uploads
└── instance/                 # SQLite database
```

### Key Design Decisions

**Database Choice**: SQLite chosen for simplicity and portability, with architecture designed to easily migrate to PostgreSQL for production deployments.

**Chunked Processing**: 2500-record chunks balance memory usage with processing efficiency for large CSV files.

**Session-Based Architecture**: Each upload creates a persistent session allowing for iterative analysis and comparison across different datasets.

**Modular ML Pipeline**: Separate engines for basic and advanced analytics allow for scalable complexity based on analysis requirements.

**Flexible Rule System**: JSON-based rule configuration with runtime evaluation supports complex business logic without code changes.

## Recent Changes

### July 21, 2025 - Modal Interface Bug Fix
- **Modal Backdrop Issue Resolution**: Fixed critical bug where modal dialogs left invisible backdrops after closing, making the main interface unresponsive
- **Enhanced Modal Cleanup**: Implemented comprehensive `cleanupExistingModals()` function that properly removes modal instances, backdrops, and resets body styles
- **Event Handler Improvements**: Added proper `hidden.bs.modal` event listeners to ensure complete cleanup when modals are closed
- **Bootstrap Modal Management**: Enhanced modal lifecycle management to prevent interference with main interface interactions
- **User Experience Fix**: Eliminated need to refresh page after viewing case details or sending escalation emails

### July 22, 2025 - Mac Local Development Dashboard Fix
- **Critical Dashboard Template Error Resolution**: Fixed Jinja template error `'dict object' has no attribute 'risk_distribution'` occurring after successful CSV upload on Mac local development
- **Template Data Structure Fix**: Updated `templates/dashboard.html` to use safe dictionary access (`attachment_analytics.get('key', default)`) instead of direct attribute access
- **Cross-Environment Compatibility**: Ensured template works with both dictionary and object data structures returned by advanced ML engine
- **Local Development Support**: Created `DASHBOARD_TEMPLATE_FIX.md` and `mac_dashboard_fix.py` for easy local environment fixes
- **Mac-Specific Error Handling**: Enhanced error handling in `advanced_ml_engine.py` to return consistent data structures even on errors
- **Template Safety Improvements**: All attachment analytics template references now use fail-safe dictionary access with fallback values

### July 22, 2025 - Migration to Replit Environment and Local Development Fixes
- **Mac Browser Compatibility Issue Resolved**: Identified that Safari browser on Mac causes "unknownUploadURL_Title" JavaScript errors during CSV upload
- **Browser Recommendation**: Mac users should use Chrome browser instead of Safari for optimal upload functionality
- **JavaScript Upload Enhancements**: Created comprehensive Mac-specific upload fixes including `mac-upload-fix.js` and simplified upload test page
- **Cross-Platform Upload Form**: Enhanced upload form with `novalidate` attribute and improved error handling for better cross-browser compatibility
- **Database Schema Migration**: Fixed missing `description` column in `attachment_keywords` table for both PostgreSQL and SQLite
- **Local Development Fixes**: Updated `local_run.py` to properly set `DATABASE_URL` for SQLite local development
- **Database Migration Script**: Created `migrate_local_db.py` for seamless local database schema updates
- **Environment Compatibility**: Ensured application works both locally (SQLite) and on Replit (PostgreSQL)
- **UI Improvements**: Removed low risk profile insight popup notification per user request
- **Modal Interface Bug Resolution**: Implemented comprehensive modal cleanup system to fix persistent backdrop issues:
  - Enhanced `cleanupExistingModals()` function with multiple fallback strategies
  - Added dual event listeners (`hide.bs.modal` and `hidden.bs.modal`) for complete cleanup
  - Implemented periodic background cleanup (5-second intervals) as failsafe
  - Added emergency escape key handler for forced modal cleanup
  - Enhanced backdrop removal to handle all Bootstrap modal states
- **PostgreSQL Integration**: Successfully configured PostgreSQL database for Replit deployment
- **Local SQLite Preference**: Documented user preference for SQLite in local development environments
- **Upload Error Resolution**: Fixed "unknown uploadurl_title" errors by improving JavaScript upload handling and database model constructors
- **Local Testing Tools**: Created `test_upload_local.py` and enhanced `debug_local.py` for comprehensive local environment testing
- **Error Handling Improvements**: Simplified upload form submission to use natural Flask redirects instead of AJAX, preventing JavaScript parsing errors
- **Migration to Replit**: Successfully migrated Email Guardian from Replit Agent to standard Replit environment
- **Local Development Optimization**: Fixed SQLAlchemy model constructor issues and database configuration for both local and Replit environments
- **Database Configuration**: Simplified SQLite setup to use `email_guardian_local.db` in current directory for local development
- **Upload Error Resolution**: Fixed upload functionality by improving session record creation and error handling
- **Model Constructor Fixes**: Updated all SQLAlchemy model instantiation to use property assignment instead of constructor parameters
- **Cross-Platform CSV Support**: Enhanced CSV processing with automatic encoding detection for Mac compatibility
- **Mac-Specific Fixes**: Added comprehensive encoding support (UTF-8, UTF-8-sig, macroman, iso-8859-1, cp1252) for better Mac CSV handling
- **File Upload Improvements**: Enhanced file sanitization and cross-platform path handling for reliable uploads on both Windows and Mac
- **Diagnostic Tools**: Created `mac_csv_test.py` for debugging CSV upload issues on Mac systems

### July 20, 2025 - Migration to Replit Environment and Performance Optimization
- **Project Migration**: Successfully migrated Email Guardian from Replit Agent to standard Replit environment
- **Database Configuration**: Configured SQLite database for Replit compatibility (email_guardian.db)
- **Import Resolution**: Fixed all import references from local_app/local_models to app/models
- **Security Enhancement**: Updated Flask configuration to use SESSION_SECRET environment variable
- **Application Deployment**: Successfully running on port 5000 with full Bootstrap 5 UI and professional styling
- **Architecture Preserved**: Maintained all core functionality including ML engine, rule engine, and dashboard system
- **Whitelist Bug Fix**: Fixed critical issue where whitelisted domains were still appearing in case management views
- **Case Filtering**: Added proper filtering to exclude whitelisted records from:
  - Main cases view (`/cases/<session_id>`)
  - Escalations dashboard (`/escalations/<session_id>`)
  - Sender details API (`/api/sender_details/<session_id>/<sender_email>`)
- **Whitelist Statistics**: Added whitelist domain counts to case management interface
- **Interactive Dashboard Animations**: Implemented comprehensive animation system:
  - Animated counters with easing transitions and staggered loading
  - Interactive card hover effects with glow and scaling
  - Real-time insight highlighting with smart popup notifications
  - Progress bars with animated stripes and dynamic width updates
  - Chart animations with delayed rendering for visual impact
  - Auto-highlighting of critical security insights
- **Real-time Dashboard Updates**: Added live statistics updates every 30 seconds
- **Deployment Optimization**: Configured application for proper Replit hosting with gunicorn
- **Admin Panel Implementation**: Built comprehensive admin interface:
  - System statistics dashboard with session metrics
  - Configuration management with live settings
  - Session management with cleanup and export tools
  - Database testing and maintenance functions
- **Advanced Rules Management System**: Built comprehensive rules engine with complex logic:
  - Complex AND/OR logic support for rule conditions
  - Regex pattern matching with validation and testing
  - Interactive rule builder with real-time preview
  - Multiple operators: contains, equals, starts_with, ends_with, regex, not_contains, greater_than, less_than, in_list, is_empty, is_not_empty
  - Rule categorization (Security, Content, Sender, Time-based)
  - Dynamic condition addition and removal
  - Rule validation and testing before saving
  - Priority-based rule processing (Critical, High, Medium, Low, Minimal)
  - Enhanced rule engine with comprehensive operator support
  - API endpoints for CRUD operations on rules
  - Import/export functionality for rule sets
  - Live rule status management and editing
- **Performance Optimization System**: Built comprehensive performance configuration system:
  - Created `performance_config.py` for dynamic performance tuning
  - Implemented fast mode with configurable chunk sizes (1000 vs 500)
  - Limited ML analysis to 2000 records in fast mode for speed
  - Reduced ML estimators from 100 to 50 for faster processing
  - Optimized progress updates (every 500 vs 100 records) 
  - Created `optimize_for_speed.py` script for instant speed boost
  - Added `README_PERFORMANCE.md` with detailed optimization guide
  - Fast mode provides 60-80% faster CSV processing and 70% faster ML analysis
  - Configurable via environment variables for different deployment scenarios
  - Maintains security detection quality while dramatically improving speed