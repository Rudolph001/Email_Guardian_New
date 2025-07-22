# Email Guardian - Service Specification

## Overview
Email security analysis platform for detecting threats, data exfiltration, and anomalous patterns in exported email data.

## Core Features

### Data Processing
- **CSV Import**: Handles large Tessian email exports with chunked processing
- **Format Support**: Flexible column mapping for various email export formats
- **Performance**: Fast mode processing (1000 records/chunk, optimized ML)

### Security Analysis
- **Rule Engine**: Configurable business rules with AND/OR logic
- **ML Detection**: Isolation Forest anomaly detection with risk scoring
- **Domain Classification**: Automatic categorization (corporate, personal, suspicious)
- **Whitelist Management**: Trust-based domain filtering

### Case Management
- **Active Cases**: Filtered view of suspicious emails requiring review
- **Risk Scoring**: Multi-dimensional assessment (0.0-1.0 scale)
- **Status Tracking**: Active, Cleared, Escalated workflow
- **Bulk Operations**: Select and process multiple cases

### Analytics Dashboards
- **Main Dashboard**: Overview statistics and trends
- **Sender Analysis**: Communication patterns by sender
- **Time Analysis**: Temporal patterns and anomalies
- **Advanced ML**: Network analysis and clustering

### Administration
- **Session Management**: Upload tracking and data persistence
- **Rule Configuration**: Dynamic rule creation and testing
- **Whitelist Control**: Domain trust management
- **System Settings**: Performance and security configuration

## Technical Stack

### Backend
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: SQLite (local) / PostgreSQL (production)
- **ML Engine**: scikit-learn (Isolation Forest, clustering)
- **Processing**: pandas with chunked CSV handling

### Frontend
- **UI**: Bootstrap 5 with responsive design
- **Charts**: Chart.js for data visualization
- **Tables**: DataTables for case management
- **Modals**: Dynamic case detail views

## Deployment Options

### Local Development
```bash
python local_run.py
# Uses SQLite, auto-configuration
# Access: http://localhost:5000
```

### Production
```bash
gunicorn --bind 0.0.0.0:5000 main:app
# Requires: DATABASE_URL, SESSION_SECRET
```

## API Endpoints

### Core Routes
- `GET /` - Dashboard overview
- `POST /upload` - CSV file upload
- `GET /cases/<session_id>` - Case management
- `GET /dashboard/<session_id>` - Analytics dashboard

### Case Management
- `POST /api/update_case_status` - Update case status
- `GET /api/sender_details/<session_id>/<email>` - Sender analysis
- `POST /api/generate_escalation_email` - Create escalation

### Administration
- `GET /admin` - System administration
- `GET /rules` - Rule management
- `POST /api/rules` - Create/update rules

## Data Flow

1. **Upload**: CSV files processed in 1000-record chunks
2. **Analysis**: Apply exclusion rules → whitelist filtering → ML scoring
3. **Storage**: Results stored with compressed session data
4. **Review**: Cases presented in filtered dashboards
5. **Action**: Clear, escalate, or investigate flagged emails

## Security Features

- **Data Isolation**: Session-based data separation
- **Rule-Based Filtering**: Pre-processing threat detection
- **ML Anomaly Detection**: Pattern-based risk assessment
- **Domain Trust Management**: Whitelist/blacklist controls
- **Case Audit Trail**: Status change tracking

## Performance Characteristics

- **Fast Mode**: 60-80% faster processing
- **Memory Efficient**: Chunked processing for large files
- **Scalable**: SQLite → PostgreSQL migration path
- **Session Persistent**: Resume analysis across sessions

## File Storage

```
uploads/          # CSV file uploads
data/            # Compressed session data
instance/        # SQLite database
static/          # Web assets
templates/       # HTML templates
```

## Environment Variables

```
DATABASE_URL     # Database connection
SESSION_SECRET   # Flask session key
FAST_MODE=true   # Performance optimization
```

## Use Cases

- **Security Teams**: Email threat investigation
- **Compliance**: Data exfiltration monitoring
- **IT Operations**: Anomalous communication detection
- **Forensics**: Email pattern analysis