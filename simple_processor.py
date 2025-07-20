"""
Simple Email Guardian processor for troubleshooting
This bypasses complex ML analysis and focuses on basic processing
"""

import pandas as pd
import logging
from datetime import datetime
from models import ProcessingSession, EmailRecord
from app import db

logger = logging.getLogger(__name__)

class SimpleProcessor:
    """Simplified processor for troubleshooting stuck sessions"""
    
    def __init__(self):
        self.chunk_size = 2000  # Larger chunks for speed
    
    def simple_process_csv(self, session_id, file_path):
        """Basic CSV processing without complex ML analysis"""
        try:
            logger.info(f"Starting simple processing for session {session_id}")
            
            # Update session status
            session = ProcessingSession.query.get(session_id)
            if session:
                session.status = 'processing'
                db.session.commit()
            
            # Count total records
            total_records = sum(1 for line in open(file_path)) - 1  # Subtract header
            if session:
                session.total_records = total_records
                db.session.commit()
            
            processed_count = 0
            
            # Process in large chunks for speed
            for chunk_df in pd.read_csv(file_path, chunksize=self.chunk_size):
                processed_count += self._process_simple_chunk(session_id, chunk_df, processed_count)
                
                # Update progress every 1000 records
                if processed_count % 1000 == 0 and session:
                    session.processed_records = processed_count
                    db.session.commit()
                    logger.info(f"Simple processing: {processed_count}/{total_records} records")
            
            # Apply basic analysis only
            self._apply_basic_analysis(session_id)
            
            # Mark as completed
            if session:
                session.status = 'completed'
                session.processed_records = processed_count
                db.session.commit()
            
            logger.info(f"Simple processing completed for session {session_id}: {processed_count} records")
            
        except Exception as e:
            logger.error(f"Error in simple processing for session {session_id}: {str(e)}")
            session = ProcessingSession.query.get(session_id)
            if session:
                session.status = 'error'
                session.error_message = f"Simple processing error: {str(e)}"
                db.session.commit()
            raise
    
    def _process_simple_chunk(self, session_id, chunk_df, start_count):
        """Process chunk with minimal analysis"""
        processed_count = 0
        
        try:
            for index, row in chunk_df.iterrows():
                try:
                    record_id = f"record_{start_count + processed_count + 1}"
                    
                    # Create basic email record
                    email_record = EmailRecord(
                        session_id=session_id,
                        record_id=record_id,
                        time=str(row.get('_time', '')),
                        sender=str(row.get('sender', '')),
                        subject=str(row.get('subject', '')),
                        attachments=str(row.get('attachments', '')),
                        recipients=str(row.get('recipients', '')),
                        recipients_email_domain=str(row.get('recipients_email_domain', '')),
                        leaver=str(row.get('leaver', '')),
                        termination_date=str(row.get('termination_date', '')),
                        wordlist_attachment=str(row.get('wordlist_attachment', '')),
                        wordlist_subject=str(row.get('wordlist_subject', '')),
                        bunit=str(row.get('bunit', '')),
                        department=str(row.get('department', '')),
                        status=str(row.get('status', '')),
                        user_response=str(row.get('user_response', '')),
                        final_outcome=str(row.get('final_outcome', '')),
                        justification=str(row.get('justification', '')),
                        # Set basic risk analysis
                        ml_risk_score=0.3,  # Default medium risk
                        risk_level='Medium'
                    )
                    
                    db.session.add(email_record)
                    processed_count += 1
                    
                except Exception as record_error:
                    logger.warning(f"Skipping record {index}: {str(record_error)}")
                    continue
            
            # Commit chunk
            db.session.commit()
            return processed_count
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error processing simple chunk: {str(e)}")
            raise
    
    def _apply_basic_analysis(self, session_id):
        """Apply basic analysis without complex ML"""
        try:
            logger.info(f"Applying basic analysis for session {session_id}")
            
            # Simple risk categorization based on keywords
            high_risk_keywords = ['confidential', 'urgent', 'invoice', 'payment', 'personal']
            
            records = EmailRecord.query.filter_by(session_id=session_id).all()
            
            for record in records:
                risk_score = 0.3  # Base medium risk
                
                # Check for high-risk patterns
                text_to_check = f"{record.subject} {record.attachments} {record.wordlist_subject} {record.wordlist_attachment}".lower()
                
                for keyword in high_risk_keywords:
                    if keyword in text_to_check:
                        risk_score += 0.2
                
                # Check if external domain
                domain = record.recipients_email_domain.lower()
                if domain and any(ext in domain for ext in ['gmail.com', 'yahoo.com', 'hotmail.com']):
                    risk_score += 0.3
                
                # Update risk level
                if risk_score > 0.8:
                    record.risk_level = 'Critical'
                elif risk_score > 0.6:
                    record.risk_level = 'High'
                elif risk_score > 0.4:
                    record.risk_level = 'Medium'
                else:
                    record.risk_level = 'Low'
                
                record.ml_risk_score = min(risk_score, 1.0)
            
            db.session.commit()
            logger.info(f"Basic analysis completed for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error in basic analysis: {str(e)}")
            raise

# Usage function
def run_simple_processing(session_id, file_path):
    """Run simple processing for a stuck session"""
    processor = SimpleProcessor()
    processor.simple_process_csv(session_id, file_path)