from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from app import app, db
from models import ProcessingSession, EmailRecord, Rule, WhitelistDomain, AttachmentKeyword, ProcessingError
from session_manager import SessionManager
from data_processor import DataProcessor
from ml_engine import MLEngine
from advanced_ml_engine import AdvancedMLEngine
from performance_config import config
from rule_engine import RuleEngine
from domain_manager import DomainManager
import uuid
import os
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Initialize core components
session_manager = SessionManager()
data_processor = DataProcessor()
ml_engine = MLEngine()
advanced_ml_engine = AdvancedMLEngine()
rule_engine = RuleEngine()
domain_manager = DomainManager()

@app.route('/')
def index():
    """Main index page with upload functionality"""
    recent_sessions = ProcessingSession.query.order_by(ProcessingSession.upload_time.desc()).limit(10).all()
    return render_template('index.html', recent_sessions=recent_sessions)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload and create processing session"""
    try:
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(url_for('index'))

        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('index'))

        if not file.filename.lower().endswith('.csv'):
            flash('Please upload a CSV file', 'error')
            return redirect(url_for('index'))

        # Create new session
        session_id = str(uuid.uuid4())
        filename = file.filename

        # Save uploaded file
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_{filename}")
        file.save(upload_path)

        # Create session record
        session = ProcessingSession(
            id=session_id,
            filename=filename,
            status='uploaded'
        )
        db.session.add(session)
        db.session.commit()

        # Process the file asynchronously (start processing and redirect immediately)
        flash(f'File uploaded successfully. Processing started. Session ID: {session_id}', 'success')

        # Start processing in background with proper Flask context
        try:
            # Quick validation only
            import threading
            def background_processing():
                with app.app_context():  # Create Flask application context
                    try:
                        data_processor.process_csv(session_id, upload_path)
                        logger.info(f"Background processing completed for session {session_id}")
                    except Exception as e:
                        logger.error(f"Background processing error for session {session_id}: {str(e)}")
                        session = ProcessingSession.query.get(session_id)
                        if session:
                            session.status = 'error'
                            session.error_message = str(e)
                            db.session.commit()

            # Start background thread
            thread = threading.Thread(target=background_processing)
            thread.daemon = True
            thread.start()

            return redirect(url_for('dashboard', session_id=session_id))
        except Exception as e:
            logger.error(f"Processing initialization error for session {session_id}: {str(e)}")
            session.status = 'error'
            session.error_message = str(e)
            db.session.commit()
            flash(f'Error starting processing: {str(e)}', 'error')
            return redirect(url_for('index'))

    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        flash(f'Upload failed: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/processing-status/<session_id>')
def processing_status(session_id):
    """Get processing status for session"""
    session = ProcessingSession.query.get_or_404(session_id)
    
    # Get workflow statistics
    workflow_stats = {}
    if session.status in ['processing', 'completed']:
        try:
            # Count excluded records
            excluded_count = EmailRecord.query.filter(
                EmailRecord.session_id == session_id,
                EmailRecord.excluded_by_rule.isnot(None)
            ).count()
            
            # Count whitelisted records  
            whitelisted_count = EmailRecord.query.filter_by(
                session_id=session_id,
                whitelisted=True
            ).count()
            
            # Count records with rule matches
            rules_matched_count = EmailRecord.query.filter(
                EmailRecord.session_id == session_id,
                EmailRecord.rule_matches.isnot(None)
            ).count()
            
            # Count critical cases
            critical_cases_count = EmailRecord.query.filter_by(
                session_id=session_id,
                risk_level='Critical'
            ).count()
            
            workflow_stats = {
                'excluded_count': excluded_count,
                'whitelisted_count': whitelisted_count,
                'rules_matched_count': rules_matched_count,
                'critical_cases_count': critical_cases_count
            }
        except Exception as e:
            logger.warning(f"Could not get workflow stats: {str(e)}")
    
    return jsonify({
        'status': session.status,
        'total_records': session.total_records or 0,
        'processed_records': session.processed_records or 0,
        'progress_percent': int((session.processed_records or 0) / max(session.total_records or 1, 1) * 100),
        'error_message': session.error_message,
        'workflow_stats': workflow_stats
    })

@app.route('/api/dashboard-stats/<session_id>')
def dashboard_stats(session_id):
    """Get real-time dashboard statistics for animations"""
    try:
        # Get basic stats
        stats = session_manager.get_processing_stats(session_id)
        ml_insights = ml_engine.get_insights(session_id)
        
        # Get real-time counts
        total_records = EmailRecord.query.filter_by(session_id=session_id).count()
        critical_cases = EmailRecord.query.filter_by(
            session_id=session_id, 
            risk_level='Critical'
        ).filter(EmailRecord.whitelisted != True).count()
        
        whitelisted_records = EmailRecord.query.filter_by(
            session_id=session_id,
            whitelisted=True
        ).count()
        
        return jsonify({
            'total_records': total_records,
            'critical_cases': critical_cases,
            'avg_risk_score': ml_insights.get('average_risk_score', 0),
            'whitelisted_records': whitelisted_records,
            'processing_complete': stats.get('session_info', {}).get('status') == 'completed',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/dashboard/<session_id>')
def dashboard(session_id):
    """Main dashboard with processing statistics and ML insights"""
    session = ProcessingSession.query.get_or_404(session_id)

    # If still processing, show processing view
    if session.status in ['uploaded', 'processing']:
        return render_template('processing.html', session=session)

    # Get processing statistics
    try:
        stats = session_manager.get_processing_stats(session_id)
    except Exception as e:
        logger.warning(f"Could not get processing stats: {str(e)}")
        stats = {}

    # Get ML insights
    try:
        ml_insights = ml_engine.get_insights(session_id)
    except Exception as e:
        logger.warning(f"Could not get ML insights: {str(e)}")
        ml_insights = {}

    # Get BAU analysis (cached to prevent repeated calls)
    try:
        # Only run analysis if session is completed and we don't have cached results
        if hasattr(session, 'bau_cached') and session.bau_cached:
            bau_analysis = session.bau_cached
        else:
            bau_analysis = advanced_ml_engine.analyze_bau_patterns(session_id)
    except Exception as e:
        logger.warning(f"Could not get BAU analysis: {str(e)}")
        bau_analysis = {}

    # Get attachment risk analytics (cached to prevent repeated calls)
    try:
        # Only run analysis if session is completed and we don't have cached results
        if hasattr(session, 'attachment_cached') and session.attachment_cached:
            attachment_analytics = session.attachment_cached
        else:
            attachment_analytics = advanced_ml_engine.analyze_attachment_risks(session_id)
    except Exception as e:
        logger.warning(f"Could not get attachment analytics: {str(e)}")
        attachment_analytics = {}

    # Get workflow statistics for the dashboard
    workflow_stats = {}
    try:
        # Count excluded records
        excluded_count = EmailRecord.query.filter(
            EmailRecord.session_id == session_id,
            EmailRecord.excluded_by_rule.isnot(None)
        ).count()
        
        # Count whitelisted records  
        whitelisted_count = EmailRecord.query.filter_by(
            session_id=session_id,
            whitelisted=True
        ).count()
        
        # Count records with rule matches
        rules_matched_count = EmailRecord.query.filter(
            EmailRecord.session_id == session_id,
            EmailRecord.rule_matches.isnot(None)
        ).count()
        
        # Count critical cases
        critical_cases_count = EmailRecord.query.filter_by(
            session_id=session_id,
            risk_level='Critical'
        ).count()
        
        workflow_stats = {
            'excluded_count': excluded_count,
            'whitelisted_count': whitelisted_count,
            'rules_matched_count': rules_matched_count,
            'critical_cases_count': critical_cases_count
        }
    except Exception as e:
        logger.warning(f"Could not get workflow stats for dashboard: {str(e)}")

    return render_template('dashboard.html', 
                         session=session, 
                         stats=stats,
                         ml_insights=ml_insights,
                         bau_analysis=bau_analysis,
                         attachment_analytics=attachment_analytics,
                         workflow_stats=workflow_stats)

@app.route('/cases/<session_id>')
def cases(session_id):
    """Case management page with advanced filtering"""
    session = ProcessingSession.query.get_or_404(session_id)

    # Get filter parameters
    page = request.args.get('page', 1, type=int)
    risk_level = request.args.get('risk_level', '')
    case_status = request.args.get('case_status', '')
    search = request.args.get('search', '')

    # Build query with filters - exclude whitelisted records from cases
    query = EmailRecord.query.filter_by(session_id=session_id).filter(
        EmailRecord.whitelisted != True
    )

    if risk_level:
        query = query.filter(EmailRecord.risk_level == risk_level)
    if case_status:
        query = query.filter(EmailRecord.case_status == case_status)
    if search:
        query = query.filter(
            db.or_(
                EmailRecord.sender.contains(search),
                EmailRecord.subject.contains(search),
                EmailRecord.recipients_email_domain.contains(search)
            )
        )

    # Apply sorting and pagination
    cases_pagination = query.order_by(EmailRecord.ml_risk_score.desc()).paginate(
        page=page, per_page=50, error_out=False
    )

    # Get whitelist statistics
    total_whitelisted = EmailRecord.query.filter_by(session_id=session_id).filter(
        EmailRecord.whitelisted == True
    ).count()
    
    active_whitelist_domains = WhitelistDomain.query.filter_by(is_active=True).count()

    return render_template('cases.html', 
                         session=session,
                         cases=cases_pagination,
                         risk_level=risk_level,
                         case_status=case_status,
                         search=search,
                         total_whitelisted=total_whitelisted,
                         active_whitelist_domains=active_whitelist_domains)

@app.route('/escalations/<session_id>')
def escalations(session_id):
    """Escalation dashboard for critical cases"""
    session = ProcessingSession.query.get_or_404(session_id)

    # Get critical and escalated cases - exclude whitelisted records
    critical_cases = EmailRecord.query.filter_by(
        session_id=session_id,
        risk_level='Critical'
    ).filter(
        EmailRecord.whitelisted != True
    ).order_by(EmailRecord.ml_risk_score.desc()).all()

    escalated_cases = EmailRecord.query.filter_by(
        session_id=session_id,
        case_status='Escalated'
    ).filter(
        EmailRecord.whitelisted != True
    ).order_by(EmailRecord.escalated_at.desc()).all()

    return render_template('escalations.html',
                         session=session,
                         critical_cases=critical_cases,
                         escalated_cases=escalated_cases)

@app.route('/sender_analysis/<session_id>')
def sender_analysis(session_id):
    """Sender behavior analysis dashboard"""
    session = ProcessingSession.query.get_or_404(session_id)
    
    try:
        analysis = advanced_ml_engine.analyze_sender_behavior(session_id)
        if not analysis or 'error' in analysis:
            # Provide default empty analysis structure
            analysis = {
                'total_senders': 0,
                'sender_profiles': {},
                'summary_statistics': {
                    'high_risk_senders': 0,
                    'external_focused_senders': 0,
                    'attachment_senders': 0,
                    'avg_emails_per_sender': 0
                }
            }
    except Exception as e:
        logger.error(f"Error in sender analysis: {str(e)}")
        analysis = {
            'total_senders': 0,
            'sender_profiles': {},
            'summary_statistics': {
                'high_risk_senders': 0,
                'external_focused_senders': 0,
                'attachment_senders': 0,
                'avg_emails_per_sender': 0
            }
        }

    return render_template('sender_analysis.html',
                         session=session,
                         analysis=analysis)

@app.route('/time_analysis/<session_id>')
def time_analysis(session_id):
    """Temporal pattern analysis dashboard"""
    session = ProcessingSession.query.get_or_404(session_id)
    analysis = advanced_ml_engine.analyze_temporal_patterns(session_id)

    return render_template('time_analysis.html',
                         session=session,
                         analysis=analysis)

@app.route('/whitelist_analysis/<session_id>')
def whitelist_analysis(session_id):
    """Domain whitelist recommendations dashboard"""
    session = ProcessingSession.query.get_or_404(session_id)
    analysis = domain_manager.analyze_whitelist_recommendations(session_id)

    return render_template('whitelist_analysis.html',
                         session=session,
                         analysis=analysis)

@app.route('/advanced_ml_dashboard/<session_id>')
def advanced_ml_dashboard(session_id):
    """Advanced ML insights and pattern recognition"""
    session = ProcessingSession.query.get_or_404(session_id)
    insights = advanced_ml_engine.get_advanced_insights(session_id)

    return render_template('advanced_ml_dashboard.html',
                         session=session,
                         insights=insights)

@app.route('/admin')
def admin():
    """Administration panel"""
    # System statistics for the new admin template
    stats = {
        'total_sessions': ProcessingSession.query.count(),
        'active_sessions': ProcessingSession.query.filter_by(status='processing').count(),
        'completed_sessions': ProcessingSession.query.filter_by(status='completed').count(),
        'failed_sessions': ProcessingSession.query.filter_by(status='failed').count()
    }
    
    # Recent sessions for the admin panel
    recent_sessions = ProcessingSession.query.order_by(ProcessingSession.upload_time.desc()).limit(5).all()
    
    # Legacy data for backward compatibility (if needed)
    sessions = ProcessingSession.query.order_by(ProcessingSession.upload_time.desc()).all()
    whitelist_domains = WhitelistDomain.query.filter_by(is_active=True).all()
    attachment_keywords = AttachmentKeyword.query.filter_by(is_active=True).all()

    # Risk scoring algorithm details for transparency
    risk_scoring_info = {
        'thresholds': {
            'critical': 0.8,
            'high': 0.6,
            'medium': 0.4,
            'low': 0.0
        },
        'algorithm_components': {
            'anomaly_detection': {
                'weight': 40,
                'description': 'Isolation Forest algorithm detects unusual patterns',
                'method': 'sklearn.ensemble.IsolationForest',
                'contamination_rate': '10%',
                'estimators': config.ml_estimators
            },
            'rule_based_factors': {
                'weight': 60,
                'factors': [
                    {'name': 'Leaver Status', 'max_score': 0.3, 'description': 'Employee leaving organization'},
                    {'name': 'External Domain', 'max_score': 0.2, 'description': 'Public email domains (Gmail, Yahoo, etc.)'},
                    {'name': 'Attachment Risk', 'max_score': 0.3, 'description': 'File type and suspicious patterns'},
                    {'name': 'Wordlist Matches', 'max_score': 0.2, 'description': 'Suspicious keywords in subject/attachment'},
                    {'name': 'Time-based Risk', 'max_score': 0.1, 'description': 'Weekend/after-hours activity'},
                    {'name': 'Justification Analysis', 'max_score': 0.1, 'description': 'Suspicious terms in explanations'}
                ]
            }
        },
        'attachment_scoring': {
            'high_risk_extensions': ['.exe', '.scr', '.bat', '.cmd', '.com', '.pif', '.vbs', '.js'],
            'high_risk_score': 0.8,
            'medium_risk_extensions': ['.zip', '.rar', '.7z', '.doc', '.docx', '.xls', '.xlsx', '.pdf'],
            'medium_risk_score': 0.3,
            'suspicious_patterns': ['double extension', 'hidden', 'confidential', 'urgent', 'invoice'],
            'pattern_score': 0.2
        },
        'performance_config': {
            'fast_mode': config.fast_mode,
            'max_ml_records': config.max_ml_records,
            'ml_estimators': config.ml_estimators,
            'tfidf_max_features': config.tfidf_max_features,
            'chunk_size': config.chunk_size
        }
    }

    return render_template('admin.html',
                         stats=stats,
                         recent_sessions=recent_sessions,
                         sessions=sessions,
                         whitelist_domains=whitelist_domains,
                         attachment_keywords=attachment_keywords,
                         risk_scoring_info=risk_scoring_info)

@app.route('/whitelist-domains')
def whitelist_domains():
    """Whitelist domains management interface"""
    return render_template('whitelist_domains.html')

@app.route('/rules')
def rules():
    """Rules management interface"""
    # Get all rules with counts for display
    security_rules = Rule.query.filter_by(rule_type='security', is_active=True).all()
    exclusion_rules = Rule.query.filter_by(rule_type='exclusion', is_active=True).all()
    
    # Get rule counts for statistics
    rule_counts = {
        'security_active': len(security_rules),
        'exclusion_active': len(exclusion_rules),
        'security_total': Rule.query.filter_by(rule_type='security').count(),
        'exclusion_total': Rule.query.filter_by(rule_type='exclusion').count()
    }

    return render_template('rules.html',
                         security_rules=security_rules,
                         exclusion_rules=exclusion_rules,
                         rule_counts=rule_counts)

@app.route('/api/rules', methods=['POST'])
def create_rule():
    """Create a new rule with complex AND/OR conditions"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'rule_type', 'conditions']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        
        # Create new rule
        rule = Rule(
            name=data['name'],
            rule_type=data['rule_type'],
            category=data.get('category', 'security'),
            description=data.get('description', ''),
            priority=data.get('priority', 50),
            conditions=data['conditions'],  # Already JSON string from frontend
            actions=data.get('actions', 'flag'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(rule)
        db.session.commit()
        
        logger.info(f"Created new rule: {rule.name} (ID: {rule.id})")
        
        return jsonify({
            'success': True,
            'message': 'Rule created successfully',
            'rule_id': rule.id
        })
        
    except Exception as e:
        logger.error(f"Error creating rule: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/rules/<int:rule_id>', methods=['PUT'])
def update_rule(rule_id):
    """Update an existing rule"""
    try:
        rule = Rule.query.get_or_404(rule_id)
        data = request.get_json()
        
        # Handle toggle functionality
        if 'is_active' in data and data['is_active'] is None:
            rule.is_active = not rule.is_active
        else:
            # Update rule fields
            for field in ['name', 'rule_type', 'category', 'description', 'priority', 'conditions', 'actions', 'is_active']:
                if field in data and data[field] is not None:
                    setattr(rule, field, data[field])
        
        rule.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Rule updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating rule {rule_id}: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/rules/<int:rule_id>', methods=['DELETE'])
def delete_rule(rule_id):
    """Delete a rule"""
    try:
        rule = Rule.query.get_or_404(rule_id)
        db.session.delete(rule)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Rule deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting rule {rule_id}: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# API Endpoints
@app.route('/api/ml_insights/<session_id>')
def api_ml_insights(session_id):
    """Get ML analysis data for dashboard charts"""
    try:
        insights = ml_engine.get_insights(session_id)
        if not insights:
            return jsonify({'error': 'No insights available'}), 404
        return jsonify(insights)
    except Exception as e:
        logger.error(f"Error getting ML insights for session {session_id}: {str(e)}")
        return jsonify({'error': 'Failed to load ML insights', 'details': str(e)}), 500

@app.route('/api/bau_analysis/<session_id>')
def api_bau_analysis(session_id):
    """Get BAU recommendations"""
    analysis = advanced_ml_engine.analyze_bau_patterns(session_id)
    return jsonify(analysis)

@app.route('/api/attachment_risk_analytics/<session_id>')
def api_attachment_risk_analytics(session_id):
    """Get attachment intelligence data"""
    analytics = advanced_ml_engine.analyze_attachment_risks(session_id)
    return jsonify(analytics)

@app.route('/api/case/<session_id>/<record_id>')
def api_case_details(session_id, record_id):
    """Get individual case details"""
    case = EmailRecord.query.filter_by(session_id=session_id, record_id=record_id).first_or_404()

    case_data = {
        'record_id': case.record_id,
        'sender': case.sender,
        'subject': case.subject,
        'recipients': case.recipients,
        'recipients_email_domain': case.recipients_email_domain,
        'attachments': case.attachments,
        'risk_level': case.risk_level,
        'ml_risk_score': case.ml_risk_score,
        'ml_explanation': case.ml_explanation,
        'rule_matches': json.loads(case.rule_matches) if case.rule_matches else [],
        'case_status': case.case_status,
        'justification': case.justification,
        'time': case.time
    }

    return jsonify(case_data)

@app.route('/api/ml-keywords')
def api_ml_keywords():
    """Get keywords used by ML engine"""
    keywords = AttachmentKeyword.query.filter_by(is_active=True).all()
    
    keyword_data = []
    for keyword in keywords:
        keyword_data.append({
            'keyword': keyword.keyword,
            'category': keyword.category,
            'risk_score': keyword.risk_score,
            'description': keyword.description,
            'is_active': keyword.is_active
        })
    
    return jsonify({
        'total_keywords': len(keyword_data),
        'keywords': keyword_data,
        'categories': {
            'Business': len([k for k in keyword_data if k['category'] == 'Business']),
            'Personal': len([k for k in keyword_data if k['category'] == 'Personal']),
            'Suspicious': len([k for k in keyword_data if k['category'] == 'Suspicious'])
        }
    })

@app.route('/api/exclusion-rules', methods=['GET', 'POST'])
def api_exclusion_rules():
    """Get all exclusion rules or create new one"""
    if request.method == 'GET':
        rules = Rule.query.filter_by(rule_type='exclusion', is_active=True).all()
        return jsonify([{
            'id': rule.id,
            'name': rule.name,
            'description': rule.description,
            'conditions': rule.conditions,
            'actions': rule.actions,
            'priority': rule.priority
        } for rule in rules])

    elif request.method == 'POST':
        data = request.get_json()
        rule = Rule(
            name=data['name'],
            description=data.get('description', ''),
            rule_type='exclusion',
            conditions=data['conditions'],
            actions=data.get('actions', {}),
            priority=data.get('priority', 1)
        )
        db.session.add(rule)
        db.session.commit()
        return jsonify({'id': rule.id, 'status': 'created'})

@app.route('/api/exclusion-rules/<int:rule_id>', methods=['GET', 'PUT', 'DELETE'])
def api_exclusion_rule(rule_id):
    """Get, update, or delete specific exclusion rule"""
    rule = Rule.query.get_or_404(rule_id)

    if request.method == 'GET':
        return jsonify({
            'id': rule.id,
            'name': rule.name,
            'description': rule.description,
            'conditions': rule.conditions,
            'actions': rule.actions,
            'priority': rule.priority,
            'is_active': rule.is_active
        })

    elif request.method == 'PUT':
        data = request.get_json()
        rule.name = data.get('name', rule.name)
        rule.description = data.get('description', rule.description)
        rule.conditions = data.get('conditions', rule.conditions)
        rule.actions = data.get('actions', rule.actions)
        rule.priority = data.get('priority', rule.priority)
        rule.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'status': 'updated'})

    elif request.method == 'DELETE':
        rule.is_active = False
        db.session.commit()
        return jsonify({'status': 'deleted'})

@app.route('/api/exclusion-rules/<int:rule_id>/toggle', methods=['POST'])
def api_toggle_exclusion_rule(rule_id):
    """Toggle rule active status"""
    rule = Rule.query.get_or_404(rule_id)
    rule.is_active = not rule.is_active
    db.session.commit()
    return jsonify({'status': 'toggled', 'is_active': rule.is_active})

@app.route('/api/whitelist-domains', methods=['GET', 'POST'])
def api_whitelist_domains():
    """Get all whitelist domains or create new one"""
    if request.method == 'GET':
        try:
            domains = WhitelistDomain.query.order_by(WhitelistDomain.added_at.desc()).all()
            return jsonify([{
                'id': domain.id,
                'domain': domain.domain,
                'domain_type': domain.domain_type or 'Corporate',
                'added_by': domain.added_by or 'System',
                'added_at': domain.added_at.isoformat() if domain.added_at else datetime.utcnow().isoformat(),
                'notes': domain.notes or '',
                'is_active': domain.is_active if domain.is_active is not None else True
            } for domain in domains])
        except Exception as e:
            logger.error(f"Error fetching whitelist domains: {str(e)}")
            return jsonify({'error': 'Failed to fetch whitelist domains', 'details': str(e)}), 500

    elif request.method == 'POST':
        try:
            data = request.get_json()
            domain = data.get('domain', '').strip().lower()
            
            if not domain:
                return jsonify({'success': False, 'message': 'Domain is required'}), 400
            
            # Check if domain already exists
            existing = WhitelistDomain.query.filter_by(domain=domain).first()
            if existing:
                return jsonify({'success': False, 'message': f'Domain {domain} already exists'}), 400
            
            whitelist_domain = WhitelistDomain(
                domain=domain,
                domain_type=data.get('domain_type', 'Corporate'),
                added_by=data.get('added_by', 'Admin'),
                notes=data.get('notes', '')
            )
            
            db.session.add(whitelist_domain)
            db.session.commit()
            
            logger.info(f"Added whitelist domain: {domain}")
            return jsonify({'success': True, 'message': f'Domain {domain} added successfully', 'id': whitelist_domain.id})
            
        except Exception as e:
            logger.error(f"Error adding whitelist domain: {str(e)}")
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/whitelist-domains/<int:domain_id>', methods=['GET', 'PUT', 'DELETE'])
def api_whitelist_domain(domain_id):
    """Get, update, or delete specific whitelist domain"""
    domain = WhitelistDomain.query.get_or_404(domain_id)

    if request.method == 'GET':
        return jsonify({
            'id': domain.id,
            'domain': domain.domain,
            'domain_type': domain.domain_type,
            'added_by': domain.added_by,
            'added_at': domain.added_at.isoformat() if domain.added_at else None,
            'notes': domain.notes,
            'is_active': domain.is_active
        })

    elif request.method == 'PUT':
        try:
            data = request.get_json()
            
            domain.domain_type = data.get('domain_type', domain.domain_type)
            domain.notes = data.get('notes', domain.notes)
            
            db.session.commit()
            
            logger.info(f"Updated whitelist domain: {domain.domain}")
            return jsonify({'success': True, 'message': 'Domain updated successfully'})
            
        except Exception as e:
            logger.error(f"Error updating whitelist domain {domain_id}: {str(e)}")
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500

    elif request.method == 'DELETE':
        try:
            domain_name = domain.domain
            db.session.delete(domain)
            db.session.commit()
            
            logger.info(f"Deleted whitelist domain: {domain_name}")
            return jsonify({'success': True, 'message': f'Domain {domain_name} deleted successfully'})
            
        except Exception as e:
            logger.error(f"Error deleting whitelist domain {domain_id}: {str(e)}")
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/whitelist-domains/<int:domain_id>/toggle', methods=['POST'])
def api_toggle_whitelist_domain(domain_id):
    """Toggle whitelist domain active status"""
    try:
        domain = WhitelistDomain.query.get_or_404(domain_id)
        domain.is_active = not domain.is_active
        db.session.commit()
        
        status = 'activated' if domain.is_active else 'deactivated'
        logger.info(f"Domain {domain.domain} {status}")
        
        return jsonify({
            'success': True, 
            'message': f'Domain {domain.domain} {status} successfully',
            'is_active': domain.is_active
        })
        
    except Exception as e:
        logger.error(f"Error toggling whitelist domain {domain_id}: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/whitelist', methods=['POST'])
def admin_update_whitelist():
    """Update whitelist domains"""
    try:
        domains = request.form.get('domains', '').strip()
        if domains:
            domain_list = [d.strip().lower() for d in domains.split('\n') if d.strip()]
            for domain in domain_list:
                if not WhitelistDomain.query.filter_by(domain=domain).first():
                    whitelist_entry = WhitelistDomain(
                        domain=domain,
                        domain_type='Corporate',
                        added_by='Admin'
                    )
                    db.session.add(whitelist_entry)
            db.session.commit()
            flash(f'Added {len(domain_list)} domains to whitelist', 'success')
        return redirect(url_for('admin'))
    except Exception as e:
        flash(f'Error updating whitelist: {str(e)}', 'error')
        return redirect(url_for('admin'))



@app.route('/api/case/<session_id>/<record_id>/status', methods=['PUT'])
def update_case_status(session_id, record_id):
    """Update case status"""
    try:
        case = EmailRecord.query.filter_by(session_id=session_id, record_id=record_id).first_or_404()
        data = request.get_json()

        case.case_status = data.get('status', case.case_status)
        case.notes = data.get('notes', case.notes)

        if data.get('status') == 'Escalated':
            case.escalated_at = datetime.utcnow()
        elif data.get('status') == 'Cleared':
            case.resolved_at = datetime.utcnow()

        db.session.commit()
        return jsonify({'status': 'updated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/escalation/<session_id>/<record_id>/generate-email')
def generate_escalation_email(session_id, record_id):
    """Generate escalation email for a case"""
    try:
        case = EmailRecord.query.filter_by(session_id=session_id, record_id=record_id).first_or_404()
        
        # Generate email content based on case details
        risk_level = case.risk_level or 'Medium'
        ml_score = case.ml_risk_score or 0.0
        
        # Use the sender email address from the case as the recipient
        to_email = case.sender
        
        subject = f'URGENT: {risk_level} Risk Email Alert - {case.sender}'
        
        # Generate email body
        body = f"""SECURITY ALERT - Immediate Action Required

Case ID: {case.record_id}
Risk Level: {risk_level}
ML Risk Score: {ml_score:.3f}

Email Details:
- Sender: {case.sender}
- Recipients: {case.recipients or 'N/A'}
- Subject: {case.subject or 'N/A'}
- Time Sent: {case.time or 'N/A'}
- Attachments: {case.attachments or 'None'}

Risk Assessment:
{case.ml_explanation or 'No explanation available'}

Recommended Actions:
"""
        
        if risk_level == 'Critical':
            body += """
1. Block sender immediately
2. Quarantine any attachments
3. Notify affected recipients
4. Conduct immediate security review
5. Document incident for compliance
"""
        elif risk_level == 'High':
            body += """
1. Review email content carefully
2. Verify sender legitimacy
3. Scan attachments for threats
4. Monitor recipient activity
5. Consider sender restrictions
"""
        else:
            body += """
1. Review case details
2. Verify business justification
3. Monitor for patterns
4. Update security policies if needed
"""
        
        body += f"""
Justification Provided: {case.justification or 'None provided'}

Case Status: {case.case_status or 'Active'}
Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

This is an automated alert from Email Guardian Security System.
Please review and take appropriate action immediately.

Email Guardian Security Team
"""
        
        email_data = {
            'to': to_email,
            'cc': 'audit@company.com',
            'subject': subject,
            'body': body,
            'priority': 'high' if risk_level in ['Critical', 'High'] else 'normal'
        }
        
        logger.info(f"Generated escalation email for case {record_id} in session {session_id}")
        return jsonify(email_data)
        
    except Exception as e:
        logger.error(f"Error generating escalation email for case {record_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/processing_errors/<session_id>')
def api_processing_errors(session_id):
    """Get processing errors for session"""
    errors = ProcessingError.query.filter_by(session_id=session_id).all()
    return jsonify([{
        'id': error.id,
        'error_type': error.error_type,
        'error_message': error.error_message,
        'timestamp': error.timestamp.isoformat(),
        'resolved': error.resolved
    } for error in errors])

@app.route('/api/sender_details/<session_id>/<sender_email>')
def api_sender_details(session_id, sender_email):
    """Get detailed sender information"""
    try:
        # Get sender analysis
        analysis = advanced_ml_engine.analyze_sender_behavior(session_id)
        
        if not analysis or 'sender_profiles' not in analysis:
            return jsonify({'error': 'No sender analysis available'}), 404
            
        sender_data = analysis['sender_profiles'].get(sender_email)
        
        if not sender_data:
            return jsonify({'error': 'Sender not found in analysis'}), 404
            
        # Get recent communications for this sender - exclude whitelisted records
        recent_records = EmailRecord.query.filter_by(
            session_id=session_id,
            sender=sender_email
        ).filter(
            EmailRecord.whitelisted != True
        ).order_by(EmailRecord.id.desc()).limit(5).all()
        
        recent_activity = []
        for record in recent_records:
            recent_activity.append({
                'record_id': record.record_id,
                'recipient_domain': record.recipients_email_domain,
                'subject': record.subject[:50] + '...' if record.subject and len(record.subject) > 50 else record.subject,
                'risk_score': record.ml_risk_score,
                'risk_level': record.risk_level,
                'has_attachments': bool(record.attachments),
                'time': record.time
            })
        
        sender_details = {
            'sender_email': sender_email,
            'profile': sender_data,
            'recent_activity': recent_activity,
            'analysis_timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(sender_details)
        
    except Exception as e:
        logger.error(f"Error getting sender details for {sender_email} in session {session_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a processing session and all associated data"""
    try:
        session = ProcessingSession.query.get_or_404(session_id)
        
        # Delete associated email records
        EmailRecord.query.filter_by(session_id=session_id).delete()
        
        # Delete processing errors
        ProcessingError.query.filter_by(session_id=session_id).delete()
        
        # Delete uploaded file if it exists
        if session.data_path and os.path.exists(session.data_path):
            os.remove(session.data_path)
        
        # Check for upload file
        upload_files = [f for f in os.listdir(app.config.get('UPLOAD_FOLDER', 'uploads')) 
                       if f.startswith(session_id)]
        for file in upload_files:
            file_path = os.path.join(app.config.get('UPLOAD_FOLDER', 'uploads'), file)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Delete session record
        db.session.delete(session)
        db.session.commit()
        
        logger.info(f"Session {session_id} deleted successfully")
        return jsonify({'status': 'deleted'})
        
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/sessions/cleanup', methods=['POST'])
def cleanup_old_sessions():
    """Delete sessions older than 30 days"""
    try:
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        old_sessions = ProcessingSession.query.filter(
            ProcessingSession.upload_time < cutoff_date
        ).all()
        
        deleted_count = 0
        for session in old_sessions:
            try:
                # Delete associated records
                EmailRecord.query.filter_by(session_id=session.id).delete()
                ProcessingError.query.filter_by(session_id=session.id).delete()
                
                # Delete files
                if session.data_path and os.path.exists(session.data_path):
                    os.remove(session.data_path)
                
                upload_files = [f for f in os.listdir(app.config.get('UPLOAD_FOLDER', 'uploads')) 
                               if f.startswith(session.id)]
                for file in upload_files:
                    file_path = os.path.join(app.config.get('UPLOAD_FOLDER', 'uploads'), file)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                
                db.session.delete(session)
                deleted_count += 1
                
            except Exception as e:
                logger.warning(f"Could not delete session {session.id}: {str(e)}")
                continue
        
        db.session.commit()
        logger.info(f"Cleaned up {deleted_count} old sessions")
        return jsonify({'status': 'completed', 'deleted_count': deleted_count})
        
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/keywords/populate', methods=['POST'])
def populate_default_keywords():
    """Populate database with default ML keywords"""
    try:
        # Check if keywords already exist
        if AttachmentKeyword.query.count() > 0:
            return jsonify({'message': 'Keywords already exist', 'count': AttachmentKeyword.query.count()})
        
        default_keywords = [
            # Suspicious keywords
            {'keyword': 'urgent', 'category': 'Suspicious', 'risk_score': 8},
            {'keyword': 'confidential', 'category': 'Suspicious', 'risk_score': 7},
            {'keyword': 'invoice', 'category': 'Suspicious', 'risk_score': 6},
            {'keyword': 'payment', 'category': 'Suspicious', 'risk_score': 7},
            {'keyword': 'wire transfer', 'category': 'Suspicious', 'risk_score': 9},
            {'keyword': 'click here', 'category': 'Suspicious', 'risk_score': 8},
            {'keyword': 'verify account', 'category': 'Suspicious', 'risk_score': 9},
            {'keyword': 'suspended', 'category': 'Suspicious', 'risk_score': 8},
            {'keyword': 'immediate action', 'category': 'Suspicious', 'risk_score': 9},
            {'keyword': 'prize', 'category': 'Suspicious', 'risk_score': 7},
            {'keyword': 'winner', 'category': 'Suspicious', 'risk_score': 7},
            {'keyword': 'free money', 'category': 'Suspicious', 'risk_score': 9},
            {'keyword': 'act now', 'category': 'Suspicious', 'risk_score': 8},
            {'keyword': 'limited time', 'category': 'Suspicious', 'risk_score': 6},
            {'keyword': 'social security', 'category': 'Suspicious', 'risk_score': 9},
            {'keyword': 'tax refund', 'category': 'Suspicious', 'risk_score': 8},
            {'keyword': 'suspended account', 'category': 'Suspicious', 'risk_score': 9},
            {'keyword': 'security alert', 'category': 'Suspicious', 'risk_score': 8},
            {'keyword': 'unusual activity', 'category': 'Suspicious', 'risk_score': 7},
            {'keyword': 'bitcoin', 'category': 'Suspicious', 'risk_score': 7},
            
            # Business keywords
            {'keyword': 'meeting', 'category': 'Business', 'risk_score': 2},
            {'keyword': 'project', 'category': 'Business', 'risk_score': 2},
            {'keyword': 'proposal', 'category': 'Business', 'risk_score': 3},
            {'keyword': 'contract', 'category': 'Business', 'risk_score': 4},
            {'keyword': 'agreement', 'category': 'Business', 'risk_score': 4},
            {'keyword': 'report', 'category': 'Business', 'risk_score': 2},
            {'keyword': 'quarterly', 'category': 'Business', 'risk_score': 2},
            {'keyword': 'budget', 'category': 'Business', 'risk_score': 3},
            {'keyword': 'forecast', 'category': 'Business', 'risk_score': 2},
            {'keyword': 'presentation', 'category': 'Business', 'risk_score': 2},
            {'keyword': 'conference', 'category': 'Business', 'risk_score': 2},
            {'keyword': 'training', 'category': 'Business', 'risk_score': 2},
            {'keyword': 'schedule', 'category': 'Business', 'risk_score': 2},
            {'keyword': 'approval', 'category': 'Business', 'risk_score': 3},
            {'keyword': 'review', 'category': 'Business', 'risk_score': 2},
            {'keyword': 'deadline', 'category': 'Business', 'risk_score': 3},
            {'keyword': 'milestone', 'category': 'Business', 'risk_score': 2},
            {'keyword': 'deliverable', 'category': 'Business', 'risk_score': 2},
            {'keyword': 'stakeholder', 'category': 'Business', 'risk_score': 2},
            {'keyword': 'compliance', 'category': 'Business', 'risk_score': 3},
            
            # Personal keywords
            {'keyword': 'birthday', 'category': 'Personal', 'risk_score': 1},
            {'keyword': 'vacation', 'category': 'Personal', 'risk_score': 2},
            {'keyword': 'holiday', 'category': 'Personal', 'risk_score': 2},
            {'keyword': 'family', 'category': 'Personal', 'risk_score': 2},
            {'keyword': 'wedding', 'category': 'Personal', 'risk_score': 2},
            {'keyword': 'party', 'category': 'Personal', 'risk_score': 2},
            {'keyword': 'lunch', 'category': 'Personal', 'risk_score': 1},
            {'keyword': 'dinner', 'category': 'Personal', 'risk_score': 1},
            {'keyword': 'weekend', 'category': 'Personal', 'risk_score': 1},
            {'keyword': 'personal', 'category': 'Personal', 'risk_score': 3},
            {'keyword': 'private', 'category': 'Personal', 'risk_score': 4},
            {'keyword': 'home', 'category': 'Personal', 'risk_score': 2},
            {'keyword': 'sick leave', 'category': 'Personal', 'risk_score': 2},
            {'keyword': 'appointment', 'category': 'Personal', 'risk_score': 2},
            {'keyword': 'doctor', 'category': 'Personal', 'risk_score': 3},
            {'keyword': 'health', 'category': 'Personal', 'risk_score': 3},
            {'keyword': 'emergency', 'category': 'Personal', 'risk_score': 5},
            {'keyword': 'resignation', 'category': 'Personal', 'risk_score': 6},
            {'keyword': 'quit', 'category': 'Personal', 'risk_score': 6},
            {'keyword': 'leave company', 'category': 'Personal', 'risk_score': 7}
        ]
        
        for keyword_data in default_keywords:
            keyword = AttachmentKeyword(
                keyword=keyword_data['keyword'],
                category=keyword_data['category'],
                risk_score=keyword_data['risk_score'],
                is_active=True
            )
            db.session.add(keyword)
        
        db.session.commit()
        
        logger.info(f"Added {len(default_keywords)} default keywords to database")
        return jsonify({
            'status': 'success', 
            'message': f'Added {len(default_keywords)} keywords',
            'count': len(default_keywords)
        })
        
    except Exception as e:
        logger.error(f"Error populating keywords: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500