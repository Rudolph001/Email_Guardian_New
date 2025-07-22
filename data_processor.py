import pandas as pd
import csv
import json
import logging
from datetime import datetime
from models import ProcessingSession, EmailRecord, ProcessingError
from session_manager import SessionManager
from rule_engine import RuleEngine
from domain_manager import DomainManager
from ml_engine import MLEngine
from performance_config import config
from app import db

logger = logging.getLogger(__name__)

class DataProcessor:
    """Handles CSV processing and workflow engine"""
    
    def __init__(self):
        self.chunk_size = config.chunk_size
        self.session_manager = SessionManager()
        self.rule_engine = RuleEngine()
        self.domain_manager = DomainManager()
        self.ml_engine = MLEngine()
        self.enable_fast_mode = config.fast_mode
        logger.info(f"DataProcessor initialized with config: {config.get_config_summary()}")
        
        # Expected CSV columns (case-insensitive matching)
        self.expected_columns = [
            '_time', 'sender', 'subject', 'attachments', 'recipients',
            'recipients_email_domain', 'leaver', 'termination_date',
            'wordlist_attachment', 'wordlist_subject', 'bunit',
            'department', 'status', 'user_response', 'final_outcome',
            'justification'
        ]
    
    def process_csv(self, session_id, file_path):
        """Main CSV processing workflow"""
        try:
            logger.info(f"Starting CSV processing for session {session_id}")
            
            # Update session status
            session = ProcessingSession.query.get(session_id)
            if session:
                session.status = 'processing'
                db.session.commit()
            
            # Step 1: Validate CSV structure (quick validation)
            column_mapping = self._validate_csv_structure(file_path)
            
            # Step 2: Count total records (optimized)
            total_records = self._count_csv_rows(file_path)
            if session:
                session.total_records = total_records
                db.session.commit()
            
            processed_count = 0
            
            # Use optimized chunk size for performance
            chunk_size = self.chunk_size if self.enable_fast_mode else min(500, self.chunk_size)
            
            # Process file in chunks with proper encoding
            encoding = getattr(self, '_working_encoding', 'utf-8')
            for chunk_df in pd.read_csv(file_path, chunksize=chunk_size, encoding=encoding):
                try:
                    processed_count += self._process_chunk(session_id, chunk_df, column_mapping, processed_count)
                    
                    # Update progress based on configuration
                    if processed_count % config.progress_update_interval == 0:
                        if session:
                            session.processed_records = processed_count
                            db.session.commit()
                except Exception as chunk_error:
                    logger.warning(f"Error processing chunk: {str(chunk_error)}")
                    continue  # Skip problematic chunks but continue processing
            
            # Step 3: Apply 4-step workflow
            self._apply_workflow(session_id)
            
            # Mark as completed
            if session:
                session.status = 'completed'
                session.processed_records = processed_count
                db.session.commit()
            
            logger.info(f"CSV processing completed for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error processing CSV for session {session_id}: {str(e)}")
            session = ProcessingSession.query.get(session_id)
            if session:
                session.status = 'error'
                session.error_message = str(e)
                db.session.commit()
            db.session.commit()
            raise
    
    def _validate_csv_structure(self, file_path):
        """Validate CSV structure and create column mapping with cross-platform support"""
        try:
            # Detect file encoding for better Mac compatibility
            import chardet
            encoding_to_use = 'utf-8'
            
            try:
                with open(file_path, 'rb') as f:
                    raw_data = f.read(10000)  # Read first 10KB to detect encoding
                encoding_result = chardet.detect(raw_data)
                detected_encoding = encoding_result.get('encoding', 'utf-8')
                if detected_encoding and encoding_result.get('confidence', 0) > 0.7:
                    encoding_to_use = detected_encoding
                logger.info(f"Detected file encoding: {detected_encoding} (confidence: {encoding_result.get('confidence', 0)})")
            except Exception as enc_error:
                logger.warning(f"Encoding detection failed: {str(enc_error)}, using UTF-8")
            
            # Try multiple encodings for Mac compatibility
            encodings_to_try = [encoding_to_use, 'utf-8', 'utf-8-sig', 'iso-8859-1', 'cp1252', 'macroman']
            
            sample_df = None
            for encoding in encodings_to_try:
                try:
                    # Read first few rows to check structure
                    sample_df = pd.read_csv(file_path, nrows=5, encoding=encoding)
                    logger.info(f"Successfully read CSV with encoding: {encoding}")
                    # Store the working encoding for later use
                    self._working_encoding = encoding
                    break
                except (UnicodeDecodeError, UnicodeError):
                    logger.warning(f"Failed to read with encoding {encoding}, trying next...")
                    continue
                except Exception as e:
                    logger.warning(f"Error reading CSV with encoding {encoding}: {str(e)}")
                    continue
            
            if sample_df is None:
                raise Exception("Could not read CSV file with any supported encoding. The file might be corrupted or in an unsupported format.")
                
            actual_columns = [col.lower().strip() for col in sample_df.columns]
            
            # Create case-insensitive column mapping
            column_mapping = {}
            missing_columns = []
            
            for expected_col in self.expected_columns:
                found = False
                for actual_col in sample_df.columns:
                    if actual_col.lower().strip() == expected_col.lower():
                        column_mapping[expected_col] = actual_col
                        found = True
                        break
                
                if not found:
                    missing_columns.append(expected_col)
            
            # Log missing columns but don't fail
            if missing_columns:
                logger.warning(f"Missing columns: {missing_columns}")
            
            logger.info(f"CSV validation successful. Column mapping: {column_mapping}")
            return column_mapping
            
        except Exception as e:
            logger.error(f"CSV validation failed: {str(e)}")
            raise ValueError(f"Invalid CSV format: {str(e)}")
    
    def _count_csv_rows(self, file_path):
        """Count total rows in CSV file with cross-platform encoding support"""
        try:
            # Use the encoding that worked during validation
            encoding = getattr(self, '_working_encoding', 'utf-8')
            with open(file_path, 'r', encoding=encoding) as f:
                reader = csv.reader(f)
                row_count = sum(1 for row in reader) - 1  # Exclude header
            return max(0, row_count)
        except Exception as e:
            logger.error(f"Error counting CSV rows: {str(e)}")
            # Fallback with encoding detection
            try:
                import chardet
                with open(file_path, 'rb') as f:
                    raw_data = f.read(10000)
                result = chardet.detect(raw_data)
                fallback_encoding = result.get('encoding', 'utf-8')
                
                with open(file_path, 'r', encoding=fallback_encoding) as f:
                    reader = csv.reader(f)
                    row_count = sum(1 for row in reader) - 1
                return max(0, row_count)
            except:
                return 0
    
    def _process_chunk(self, session_id, chunk_df, column_mapping, start_index):
        """Process a chunk of CSV data"""
        try:
            processed_count = 0
            
            for index, row in chunk_df.iterrows():
                try:
                    # Create unique record ID
                    record_id = f"{session_id}_{start_index + processed_count}"
                    
                    # Map columns and normalize data
                    record_data = {}
                    for expected_col, actual_col in column_mapping.items():
                        if actual_col in row:
                            value = row[actual_col]
                            # Convert to string and normalize
                            if pd.notna(value):
                                record_data[expected_col] = str(value).lower().strip()
                            else:
                                record_data[expected_col] = ''
                    
                    # Create EmailRecord with property assignment
                    email_record = EmailRecord()
                    email_record.session_id = session_id
                    email_record.record_id = record_id
                    email_record.time = record_data.get('_time', '')
                    email_record.sender = record_data.get('sender', '')
                    email_record.subject = record_data.get('subject', '')
                    email_record.attachments = record_data.get('attachments', '')
                    email_record.recipients = record_data.get('recipients', '')
                    email_record.recipients_email_domain = record_data.get('recipients_email_domain', '')
                    email_record.leaver = record_data.get('leaver', '')
                    email_record.termination_date = record_data.get('termination_date', '')
                    email_record.wordlist_attachment = record_data.get('wordlist_attachment', '')
                    email_record.wordlist_subject = record_data.get('wordlist_subject', '')
                    email_record.bunit = record_data.get('bunit', '')
                    email_record.department = record_data.get('department', '')
                    email_record.status = record_data.get('status', '')
                    email_record.user_response = record_data.get('user_response', '')
                    email_record.final_outcome = record_data.get('final_outcome', '')
                    email_record.justification = record_data.get('justification', '')
                    
                    db.session.add(email_record)
                    processed_count += 1
                    
                except Exception as e:
                    # Log individual record errors with property assignment
                    error = ProcessingError()
                    error.session_id = session_id
                    error.error_type = 'record_processing'
                    error.error_message = str(e)
                    error.record_data = str({'index': index, 'data': row.to_dict()})
                    db.session.add(error)
                    logger.warning(f"Error processing record at index {index}: {str(e)}")
            
            # Commit chunk with error handling
            try:
                db.session.commit()
                logger.info(f"Processed chunk: {processed_count} records")
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error committing chunk: {str(e)}")
                raise
            return processed_count
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error processing chunk: {str(e)}")
            raise
    
    def _apply_workflow(self, session_id):
        """Apply 4-step processing workflow"""
        try:
            logger.info(f"Applying workflow for session {session_id}")
            
            # Step 1: Apply Exclusion Rules
            self._apply_exclusion_rules(session_id)
            
            # Step 2: Apply Whitelist Filtering
            self._apply_whitelist_filtering(session_id)
            
            # Step 3: Apply Security Rules
            self._apply_security_rules(session_id)
            
            # Step 4: Apply ML Analysis
            self._apply_ml_analysis(session_id)
            
            logger.info(f"Workflow completed for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error applying workflow for session {session_id}: {str(e)}")
            raise
    
    def _apply_exclusion_rules(self, session_id):
        """Step 1: Apply exclusion rules to filter records"""
        try:
            logger.info(f"Applying exclusion rules for session {session_id}")
            
            # Get all active exclusion rules
            excluded_count = self.rule_engine.apply_exclusion_rules(session_id)
            
            # Update session
            session = ProcessingSession.query.get(session_id)
            if session:
                session.exclusion_applied = True
                db.session.commit()
            
            logger.info(f"Exclusion rules applied: {excluded_count} records excluded")
            
        except Exception as e:
            logger.error(f"Error applying exclusion rules: {str(e)}")
            raise
    
    def _apply_whitelist_filtering(self, session_id):
        """Step 2: Apply whitelist filtering"""
        try:
            logger.info(f"Applying whitelist filtering for session {session_id}")
            
            whitelisted_count = self.domain_manager.apply_whitelist_filtering(session_id)
            
            # Update session
            session = ProcessingSession.query.get(session_id)
            if session:
                session.whitelist_applied = True
                db.session.commit()
            
            logger.info(f"Whitelist filtering applied: {whitelisted_count} records whitelisted")
            
        except Exception as e:
            logger.error(f"Error applying whitelist filtering: {str(e)}")
            raise
    
    def _apply_security_rules(self, session_id):
        """Step 3: Apply security rules"""
        try:
            logger.info(f"Applying security rules for session {session_id}")
            
            rule_matches = self.rule_engine.apply_security_rules(session_id)
            
            # Update session
            session = ProcessingSession.query.get(session_id)
            if session:
                session.rules_applied = True
                db.session.commit()
            
            logger.info(f"Security rules applied: {len(rule_matches)} rule matches found")
            
        except Exception as e:
            logger.error(f"Error applying security rules: {str(e)}")
            raise
    
    def _apply_ml_analysis(self, session_id):
        """Step 4: Apply ML analysis"""
        try:
            logger.info(f"Applying ML analysis for session {session_id}")
            
            analysis_results = self.ml_engine.analyze_session(session_id)
            
            # Update session
            session = ProcessingSession.query.get(session_id)
            if session:
                session.ml_applied = True
                session.processing_stats = analysis_results.get('processing_stats', {})
                db.session.commit()
            
            logger.info(f"ML analysis completed for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error applying ML analysis: {str(e)}")
            raise
    
    def reprocess_session(self, session_id, skip_stages=None):
        """Reprocess a session with updated rules"""
        try:
            skip_stages = skip_stages or []
            
            logger.info(f"Reprocessing session {session_id}, skipping stages: {skip_stages}")
            
            # Reset processing flags
            session = ProcessingSession.query.get(session_id)
            if session and 'exclusion' not in skip_stages:
                session.exclusion_applied = False
                # Clear exclusion results
                EmailRecord.query.filter_by(session_id=session_id).update({
                    'excluded_by_rule': None
                })
            
            if session and 'whitelist' not in skip_stages:
                session.whitelist_applied = False
                # Clear whitelist results
                EmailRecord.query.filter_by(session_id=session_id).update({
                    'whitelisted': False
                })
            
            if session and 'rules' not in skip_stages:
                session.rules_applied = False
                # Clear rule matches
                EmailRecord.query.filter_by(session_id=session_id).update({
                    'rule_matches': None
                })
            
            if session and 'ml' not in skip_stages:
                session.ml_applied = False
                # Clear ML results
                EmailRecord.query.filter_by(session_id=session_id).update({
                    'ml_risk_score': None,
                    'ml_anomaly_score': None,
                    'risk_level': None,
                    'ml_explanation': None
                })
            
            db.session.commit()
            
            # Apply workflow again
            self._apply_workflow(session_id)
            
            logger.info(f"Session {session_id} reprocessed successfully")
            
        except Exception as e:
            logger.error(f"Error reprocessing session {session_id}: {str(e)}")
            raise
