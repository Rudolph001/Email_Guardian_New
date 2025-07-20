"""
Local models for standalone Email Guardian application
This avoids circular import issues by defining models directly
"""

from datetime import datetime
from sqlalchemy import Text, JSON
from local_app import db

class ProcessingSession(db.Model):
    __tablename__ = 'processing_sessions'
    
    id = db.Column(db.String(36), primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    total_records = db.Column(db.Integer, default=0)
    processed_records = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='uploaded')  # uploaded, processing, completed, error
    error_message = db.Column(Text)
    processing_stats = db.Column(JSON)
    data_path = db.Column(db.String(500))
    is_compressed = db.Column(db.Boolean, default=False)
    
    # Processing workflow stages
    exclusion_applied = db.Column(db.Boolean, default=False)
    whitelist_applied = db.Column(db.Boolean, default=False)
    rules_applied = db.Column(db.Boolean, default=False)
    ml_applied = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<ProcessingSession {self.id}>'

class EmailRecord(db.Model):
    __tablename__ = 'email_records'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey('processing_sessions.id'), nullable=False)
    record_id = db.Column(db.String(100), nullable=False)  # Unique within session
    
    # Original CSV fields
    time = db.Column(db.String(100))
    sender = db.Column(db.String(255))
    subject = db.Column(Text)
    attachments = db.Column(Text)
    recipients = db.Column(Text)
    recipients_email_domain = db.Column(db.String(255))
    leaver = db.Column(db.String(10))
    termination_date = db.Column(db.String(100))
    wordlist_attachment = db.Column(Text)
    wordlist_subject = db.Column(Text)
    bunit = db.Column(db.String(255))
    department = db.Column(db.String(255))
    status = db.Column(db.String(100))
    user_response = db.Column(Text)
    final_outcome = db.Column(db.String(255))
    justification = db.Column(Text)
    
    # Processing results
    excluded_by_rule = db.Column(db.String(500))
    whitelisted_domain = db.Column(db.String(255))
    rule_violations = db.Column(JSON)
    risk_score = db.Column(db.Float, default=0.0)
    risk_category = db.Column(db.String(50))
    ml_anomaly_score = db.Column(db.Float)
    ml_cluster = db.Column(db.String(50))
    
    # Case management
    case_status = db.Column(db.String(50), default='open')  # open, investigating, resolved, escalated
    assigned_to = db.Column(db.String(255))
    investigation_notes = db.Column(Text)
    escalation_reason = db.Column(Text)
    resolution_action = db.Column(Text)
    
    def __repr__(self):
        return f'<EmailRecord {self.id}: {self.sender}>'

class Rule(db.Model):
    __tablename__ = 'rules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(Text)
    rule_type = db.Column(db.String(50), nullable=False)  # exclusion, scoring, flagging
    conditions = db.Column(JSON, nullable=False)
    actions = db.Column(JSON)
    priority = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Rule {self.id}: {self.name}>'

class WhitelistDomain(db.Model):
    __tablename__ = 'whitelist_domains'
    
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), nullable=False, unique=True)
    domain_type = db.Column(db.String(50))  # corporate, partner, trusted, etc.
    trust_level = db.Column(db.String(50), default='medium')  # low, medium, high
    reason = db.Column(Text)
    added_by = db.Column(db.String(255))
    added_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_verified = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Statistics
    email_count = db.Column(db.Integer, default=0)
    risk_score_avg = db.Column(db.Float, default=0.0)
    
    def __repr__(self):
        return f'<WhitelistDomain {self.domain}>'

class AttachmentKeyword(db.Model):
    __tablename__ = 'attachment_keywords'
    
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100))  # financial, personal, confidential, etc.
    risk_weight = db.Column(db.Float, default=1.0)
    is_regex = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AttachmentKeyword {self.keyword}>'

class ProcessingError(db.Model):
    __tablename__ = 'processing_errors'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey('processing_sessions.id'), nullable=False)
    error_type = db.Column(db.String(100), nullable=False)
    error_message = db.Column(Text, nullable=False)
    error_details = db.Column(JSON)
    record_data = db.Column(JSON)  # The record that caused the error
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_resolved = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<ProcessingError {self.id}: {self.error_type}>'