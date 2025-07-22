# Email Guardian - Service Specification

## Overview
Web-based email security analysis platform that processes exported email data to detect threats, data exfiltration, and anomalous communication patterns using rule-based filtering and machine learning.

## Core Capabilities

### Data Processing
- **CSV Import**: Handles large Tessian email exports with flexible column mapping
- **Chunked Processing**: 1000 records per batch for memory efficiency
- **Format Flexibility**: Adapts to various email export formats automatically
- **Session Management**: Persistent data storage with gzip compression for large datasets
- **Performance Mode**: Fast processing option (60-80% speed improvement)

### Threat Detection
- **Rule Engine**: Configurable business rules with complex AND/OR logic
- **ML Anomaly Detection**: Isolation Forest algorithm for pattern recognition
- **Risk Scoring**: Multi-dimensional assessment (0.0-1.0 scale) based on content, sender, and behavior
- **Domain Classification**: Automatic categorization (corporate, personal, public, suspicious)
- **Exclusion Filtering**: Pre-processing rules to filter out known-good communications

### Case Management
- **Active Cases**: Filtered view of emails requiring security review
- **Status Workflow**: Active → Cleared/Escalated tracking system
- **Bulk Operations**: Select and process multiple cases simultaneously
- **Case Details**: Full email content, attachments, and metadata analysis
- **Escalation Support**: Generate investigation emails with case context

### Analytics & Reporting
- **Main Dashboard**: Real-time statistics with animated counters and insights
- **Sender Analysis**: Communication patterns, frequency, and risk profiles
- **Time Analysis**: Temporal patterns and anomaly detection over time periods
- **Advanced ML Dashboard**: Network analysis, clustering, and pattern visualization
- **Whitelist Analytics**: Domain trust analysis and recommendation engine

### Administration
- **Rule Configuration**: Dynamic rule creation with regex support and testing
- **Whitelist Management**: Domain trust control with bulk import/export
- **Session Control**: Upload tracking, data cleanup, and session lifecycle
- **System Settings**: Performance tuning, security configuration
- **User Management**: Case assignment and access control

## Technical Architecture
- **Backend**: Flask + SQLAlchemy + scikit-learn ML engine
- **Database**: SQLite (local) / PostgreSQL (production)
- **Frontend**: Bootstrap 5 + Chart.js + DataTables
- **Processing**: Chunked CSV handling (1000 records/batch)

## Key Endpoints
```
POST /upload                          # CSV file upload
GET  /cases/<session_id>              # Case management interface
GET  /dashboard/<session_id>          # Analytics dashboard  
POST /api/update_case_status          # Clear/escalate cases
GET  /admin                           # System administration
```

## Deployment
```bash
# Local Development
python local_run.py                   # SQLite, port 5000

# Production  
gunicorn --bind 0.0.0.0:5000 main:app # Requires DATABASE_URL
```

## Data Flow
CSV Upload → Rule Filtering → ML Analysis → Case Review → Action (Clear/Escalate)

![Process Flow Diagram](static/images/process_flow.svg)

## Security Features
- Session-based data isolation
- Configurable rule engine (AND/OR logic)
- ML risk scoring (0.0-1.0 scale)  
- Domain whitelist/trust management
- Case audit trail

## Performance
- Fast mode: 60-80% processing speed improvement
- Memory efficient: Chunked processing for large files
- Scalable: SQLite → PostgreSQL migration ready

## Target Users
Security teams, compliance officers, IT operations, digital forensics investigators