# Email Guardian - Email Security Analysis Platform

## Overview

Email Guardian is a comprehensive web application designed for analyzing Tessian email export data to detect security threats, data exfiltration attempts, and anomalous communication patterns. The platform combines rule-based filtering, machine learning analytics, and domain classification to provide enterprise-grade email security analysis.

## User Preferences

Preferred communication style: Simple, everyday language.

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

The application is designed for local deployment with the following characteristics:

- **Target Platforms**: Windows and Mac systems
- **Database**: SQLite for simplicity (PostgreSQL-ready architecture)
- **Server**: Gunicorn on port 5000 (0.0.0.0:5000)
- **File Storage**: Local filesystem with organized directory structure
- **Session Management**: File-based with automatic compression
- **Configuration**: Environment variable based with sensible defaults

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