#!/usr/bin/env python3
"""
Debug script for Email Guardian processing issues
Run this to check processing status and fix stuck sessions
"""

from app import app, db
from models import ProcessingSession, EmailRecord
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_processing_status():
    """Check status of all processing sessions"""
    with app.app_context():
        sessions = ProcessingSession.query.all()
        
        print(f"📊 Found {len(sessions)} processing sessions:")
        print("-" * 60)
        
        for session in sessions:
            record_count = EmailRecord.query.filter_by(session_id=session.id).count()
            
            print(f"Session: {session.id[:8]}...")
            print(f"  File: {session.filename}")
            print(f"  Status: {session.status}")
            print(f"  Total Records: {session.total_records}")
            print(f"  Processed: {session.processed_records}")
            print(f"  DB Records: {record_count}")
            print(f"  Exclusion Applied: {session.exclusion_applied}")
            print(f"  Whitelist Applied: {session.whitelist_applied}")
            print(f"  Rules Applied: {session.rules_applied}")
            print(f"  ML Applied: {session.ml_applied}")
            
            if session.error_message:
                print(f"  ❌ Error: {session.error_message}")
            
            print("-" * 60)

def fix_stuck_sessions():
    """Fix sessions that are stuck in processing state"""
    with app.app_context():
        stuck_sessions = ProcessingSession.query.filter_by(status='processing').all()
        
        print(f"🔧 Found {len(stuck_sessions)} stuck processing sessions")
        
        for session in stuck_sessions:
            record_count = EmailRecord.query.filter_by(session_id=session.id).count()
            
            if record_count > 0 and session.processed_records > 0:
                # Session has records, mark as completed
                session.status = 'completed'
                print(f"✅ Fixed session {session.id[:8]}... -> completed")
            else:
                # Session has no records, mark as error
                session.status = 'error'
                session.error_message = 'Processing incomplete - no records found'
                print(f"❌ Fixed session {session.id[:8]}... -> error")
        
        db.session.commit()
        print("🎯 All stuck sessions fixed!")

def clean_empty_sessions():
    """Clean up sessions with no records"""
    with app.app_context():
        all_sessions = ProcessingSession.query.all()
        empty_sessions = []
        
        for session in all_sessions:
            record_count = EmailRecord.query.filter_by(session_id=session.id).count()
            if record_count == 0 and session.status not in ['uploaded', 'processing']:
                empty_sessions.append(session)
        
        print(f"🧹 Found {len(empty_sessions)} empty sessions to clean")
        
        for session in empty_sessions:
            print(f"Deleting empty session: {session.id[:8]}... ({session.filename})")
            db.session.delete(session)
        
        db.session.commit()
        print("✨ Empty sessions cleaned!")

def reset_session_processing(session_id):
    """Reset a specific session to allow reprocessing"""
    with app.app_context():
        session = ProcessingSession.query.get(session_id)
        if not session:
            print(f"❌ Session {session_id} not found")
            return
        
        print(f"🔄 Resetting session {session_id[:8]}...")
        
        # Reset all processing flags
        session.status = 'uploaded'
        session.exclusion_applied = False
        session.whitelist_applied = False
        session.rules_applied = False
        session.ml_applied = False
        session.error_message = None
        
        # Clear all processing results from records
        EmailRecord.query.filter_by(session_id=session_id).update({
            'excluded_by_rule': None,
            'whitelisted': False,
            'rule_matches': None,
            'ml_risk_score': None,
            'ml_anomaly_score': None,
            'risk_level': None,
            'ml_explanation': None
        })
        
        db.session.commit()
        print(f"✅ Session {session_id[:8]}... reset successfully")

if __name__ == "__main__":
    print("🔍 Email Guardian Processing Debugger")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Check processing status")
        print("2. Fix stuck sessions")
        print("3. Clean empty sessions")
        print("4. Reset specific session")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            check_processing_status()
        elif choice == '2':
            fix_stuck_sessions()
        elif choice == '3':
            clean_empty_sessions()
        elif choice == '4':
            session_id = input("Enter session ID: ").strip()
            reset_session_processing(session_id)
        elif choice == '5':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option, please try again")