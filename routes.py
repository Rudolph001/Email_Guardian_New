from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from app import app, db
from models import ProcessingSession, EmailRecord, Rule, WhitelistDomain, AttachmentKeyword, ProcessingError
from session_manager import SessionManager
from data_processor import DataProcessor
from ml_engine import MLEngine
from advanced_ml_engine import AdvancedMLEngine
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
        
        # Start processing in background (for now, we'll process synchronously but optimize it)
        try:
            # Quick validation only
            import threading
            def background_processing():
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
    return {
        'status': session.status,
        'total_records': session.total_records or 0,
        'processed_records': session.processed_records or 0,
        'progress_percent': int((session.processed_records or 0) / max(session.total_records or 1, 1) * 100),
        'error_message': session.error_message
    }

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
    
    # Get BAU analysis
    try:
        bau_analysis = advanced_ml_engine.analyze_bau_patterns(session_id)
    except Exception as e:
        logger.warning(f"Could not get BAU analysis: {str(e)}")
        bau_analysis = {}
    
    # Get attachment risk analytics
    try:
        attachment_analytics = advanced_ml_engine.analyze_attachment_risks(session_id)
    except Exception as e:
        logger.warning(f"Could not get attachment analytics: {str(e)}")
        attachment_analytics = {}
    
    return render_template('dashboard.html', 
                         session=session, 
                         stats=stats,
                         ml_insights=ml_insights,
                         bau_analysis=bau_analysis,
                         attachment_analytics=attachment_analytics)

@app.route('/cases/<session_id>')
def cases(session_id):
    """Case management page with advanced filtering"""
    session = ProcessingSession.query.get_or_404(session_id)
    
    # Get filter parameters
    page = request.args.get('page', 1, type=int)
    risk_level = request.args.get('risk_level', '')
    case_status = request.args.get('case_status', '')
    search = request.args.get('search', '')
    
    # Build query with filters
    query = EmailRecord.query.filter_by(session_id=session_id)
    
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
    
    return render_template('cases.html', 
                         session=session,
                         cases=cases_pagination,
                         risk_level=risk_level,
                         case_status=case_status,
                         search=search)

@app.route('/escalations/<session_id>')
def escalations(session_id):
    """Escalation dashboard for critical cases"""
    session = ProcessingSession.query.get_or_404(session_id)
    
    # Get critical and escalated cases
    critical_cases = EmailRecord.query.filter_by(
        session_id=session_id,
        risk_level='Critical'
    ).order_by(EmailRecord.ml_risk_score.desc()).all()
    
    escalated_cases = EmailRecord.query.filter_by(
        session_id=session_id,
        case_status='Escalated'
    ).order_by(EmailRecord.escalated_at.desc()).all()
    
    return render_template('escalations.html',
                         session=session,
                         critical_cases=critical_cases,
                         escalated_cases=escalated_cases)

@app.route('/sender_analysis/<session_id>')
def sender_analysis(session_id):
    """Sender behavior analysis dashboard"""
    session = ProcessingSession.query.get_or_404(session_id)
    analysis = advanced_ml_engine.analyze_sender_behavior(session_id)
    
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
    sessions = ProcessingSession.query.order_by(ProcessingSession.upload_time.desc()).all()
    whitelist_domains = WhitelistDomain.query.filter_by(is_active=True).all()
    attachment_keywords = AttachmentKeyword.query.filter_by(is_active=True).all()
    
    return render_template('admin.html',
                         sessions=sessions,
                         whitelist_domains=whitelist_domains,
                         attachment_keywords=attachment_keywords)

@app.route('/rules')
def rules():
    """Rules management interface"""
    security_rules = Rule.query.filter_by(rule_type='security', is_active=True).all()
    exclusion_rules = Rule.query.filter_by(rule_type='exclusion', is_active=True).all()
    
    return render_template('rules.html',
                         security_rules=security_rules,
                         exclusion_rules=exclusion_rules)

# API Endpoints
@app.route('/api/ml_insights/<session_id>')
def api_ml_insights(session_id):
    """Get ML analysis data for dashboard charts"""
    insights = ml_engine.get_insights(session_id)
    return jsonify(insights)

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

@app.route('/rules/create', methods=['POST'])
def create_rule():
    """Create new security rule"""
    try:
        rule_data = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'rule_type': request.form.get('rule_type', 'security'),
            'conditions': json.loads(request.form.get('conditions', '{}')),
            'actions': json.loads(request.form.get('actions', '{}')),
            'priority': int(request.form.get('priority', 1))
        }
        
        rule = Rule(**rule_data)
        db.session.add(rule)
        db.session.commit()
        
        flash(f'Rule "{rule.name}" created successfully', 'success')
        return redirect(url_for('rules'))
    except Exception as e:
        flash(f'Error creating rule: {str(e)}', 'error')
        return redirect(url_for('rules'))

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

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
