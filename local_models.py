# Email Guardian - Local Models (Standalone for local development)
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
import json

Base = declarative_base()

class ProcessingSession(Base):
    __tablename__ = 'processing_sessions'
    
    id = Column(String(36), primary_key=True)
    filename = Column(String(255), nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow)
    total_records = Column(Integer, default=0)
    processed_records = Column(Integer, default=0)
    status = Column(String(50), default='uploaded')  # uploaded, processing, completed, error
    error_message = Column(Text)
    processing_stats = Column(JSON)
    data_path = Column(String(500))
    is_compressed = Column(Boolean, default=False)
    
    # Processing workflow stages
    exclusion_applied = Column(Boolean, default=False)
    whitelist_applied = Column(Boolean, default=False)
    rules_applied = Column(Boolean, default=False)
    ml_applied = Column(Boolean, default=False)
    
    def __repr__(self):
        return f'<ProcessingSession {self.id}>'

class EmailRecord(Base):
    __tablename__ = 'email_records'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(36), ForeignKey('processing_sessions.id'), nullable=False)
    record_id = Column(String(100), nullable=False)  # Unique within session
    
    # Basic email fields
    sender = Column(String(255))
    recipient = Column(String(255))
    subject = Column(Text)
    timestamp = Column(DateTime)
    message_size = Column(Integer)
    
    # Analysis fields
    sender_domain = Column(String(255))
    recipient_domain = Column(String(255))
    is_internal = Column(Boolean, default=False)
    is_external = Column(Boolean, default=False)
    
    # Risk assessment
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String(20))  # Low, Medium, High, Critical
    risk_factors = Column(JSON)
    
    # ML analysis results
    anomaly_score = Column(Float)
    cluster_id = Column(Integer)
    is_anomaly = Column(Boolean, default=False)
    
    # Case management
    case_status = Column(String(50), default='new')  # new, reviewed, escalated, closed
    assigned_to = Column(String(100))
    notes = Column(Text)
    escalated_at = Column(DateTime)
    resolved_at = Column(DateTime)
    
    # Processing flags
    excluded = Column(Boolean, default=False)
    whitelisted = Column(Boolean, default=False)
    rule_matched = Column(String(100))
    
    # Attachment information
    has_attachments = Column(Boolean, default=False)
    attachment_count = Column(Integer, default=0)
    attachment_types = Column(JSON)
    attachment_risk_score = Column(Float, default=0.0)
    
    def __repr__(self):
        return f'<EmailRecord {self.record_id}>'

class Rule(Base):
    __tablename__ = 'rules'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    rule_type = Column(String(50), nullable=False)  # exclusion, security, escalation
    field = Column(String(100), nullable=False)
    operator = Column(String(20), nullable=False)  # equals, contains, regex, etc.
    value = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Rule {self.name}>'

class WhitelistDomain(Base):
    __tablename__ = 'whitelist_domains'
    
    id = Column(Integer, primary_key=True)
    domain = Column(String(255), unique=True, nullable=False)
    trust_score = Column(Float, default=1.0)
    auto_recommended = Column(Boolean, default=False)
    communication_count = Column(Integer, default=0)
    last_seen = Column(DateTime)
    added_at = Column(DateTime, default=datetime.utcnow)
    added_by = Column(String(100))
    
    def __repr__(self):
        return f'<WhitelistDomain {self.domain}>'

class AttachmentKeyword(Base):
    __tablename__ = 'attachment_keywords'
    
    id = Column(Integer, primary_key=True)
    keyword = Column(String(255), unique=True, nullable=False)
    risk_weight = Column(Float, default=1.0)
    category = Column(String(50))  # malware, suspicious, legitimate
    
    def __repr__(self):
        return f'<AttachmentKeyword {self.keyword}>'

class ProcessingError(Base):
    __tablename__ = 'processing_errors'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(36), ForeignKey('processing_sessions.id'), nullable=False)
    error_type = Column(String(100), nullable=False)
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text)
    record_id = Column(String(100))  # If error is related to specific record
    timestamp = Column(DateTime, default=datetime.utcnow)
    resolved = Column(Boolean, default=False)
    
    def __repr__(self):
        return f'<ProcessingError {self.error_type}>'