# Email Guardian - Service Specification

## Overview
Web-based email security analysis platform that processes exported email data to detect threats, data exfiltration, and anomalous communication patterns using rule-based filtering and machine learning.

## Core Capabilities
- **Data Processing**: Import & analyze large CSV email exports (Tessian format)
- **Threat Detection**: Rule engine + ML anomaly detection with risk scoring
- **Case Management**: Review, clear, or escalate suspicious emails
- **Analytics**: Dashboards for sender analysis, time patterns, and trends
- **Administration**: Rule configuration, whitelist management, session control

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