import json
import re
import logging
from datetime import datetime
from models import Rule, EmailRecord
from app import db

logger = logging.getLogger(__name__)

class RuleEngine:
    """Business rules and exclusion engine for email processing"""
    
    def __init__(self):
        self.supported_operators = [
            'equals', 'contains', 'not_equals', 'starts_with', 'ends_with',
            'in_list', 'greater_than', 'less_than', 'matches_pattern', 'is_empty', 'is_not_empty'
        ]
        
        self.supported_fields = [
            'sender', 'subject', 'attachments', 'recipients', 'recipients_email_domain',
            'leaver', 'termination_date', 'wordlist_attachment', 'wordlist_subject',
            'bunit', 'department', 'status', 'user_response', 'final_outcome', 'justification'
        ]
    
    def apply_exclusion_rules(self, session_id):
        """Apply exclusion rules to filter records before processing"""
        try:
            logger.info(f"Applying exclusion rules for session {session_id}")
            
            # Get all active exclusion rules
            exclusion_rules = Rule.query.filter_by(
                rule_type='exclusion',
                is_active=True
            ).order_by(Rule.priority.desc()).all()
            
            if not exclusion_rules:
                logger.info("No exclusion rules found")
                return 0
            
            # Get all records for the session
            records = EmailRecord.query.filter_by(session_id=session_id).all()
            excluded_count = 0
            
            for record in records:
                if record.excluded_by_rule:  # Already excluded
                    continue
                
                for rule in exclusion_rules:
                    if self._evaluate_rule_conditions(record, rule):
                        record.excluded_by_rule = rule.name
                        excluded_count += 1
                        logger.debug(f"Record {record.record_id} excluded by rule: {rule.name}")
                        break  # First matching rule excludes the record
            
            db.session.commit()
            logger.info(f"Exclusion rules applied: {excluded_count} records excluded")
            return excluded_count
            
        except Exception as e:
            logger.error(f"Error applying exclusion rules: {str(e)}")
            db.session.rollback()
            raise
    
    def apply_security_rules(self, session_id):
        """Apply security rules to detect threats and violations"""
        try:
            logger.info(f"Applying security rules for session {session_id}")
            
            # Get all active security rules
            security_rules = Rule.query.filter_by(
                rule_type='security',
                is_active=True
            ).order_by(Rule.priority.desc()).all()
            
            if not security_rules:
                logger.info("No security rules found")
                return []
            
            # Get non-excluded, non-whitelisted records
            records = EmailRecord.query.filter(
                EmailRecord.session_id == session_id,
                EmailRecord.excluded_by_rule.is_(None),
                EmailRecord.whitelisted == False
            ).all()
            
            rule_matches = []
            
            for record in records:
                matched_rules = []
                
                for rule in security_rules:
                    if self._evaluate_rule_conditions(record, rule):
                        matched_rules.append({
                            'rule_id': rule.id,
                            'rule_name': rule.name,
                            'description': rule.description,
                            'priority': rule.priority,
                            'actions': rule.actions
                        })
                        
                        # Apply rule actions
                        self._apply_rule_actions(record, rule)
                
                if matched_rules:
                    record.rule_matches = json.dumps(matched_rules)
                    rule_matches.extend(matched_rules)
                    
                    # Mark as Critical if any security rule matches
                    if not record.risk_level or record.risk_level != 'Critical':
                        record.risk_level = 'Critical'
                        record.ml_risk_score = max(record.ml_risk_score or 0, 0.9)
            
            db.session.commit()
            logger.info(f"Security rules applied: {len(rule_matches)} rule matches found")
            return rule_matches
            
        except Exception as e:
            logger.error(f"Error applying security rules: {str(e)}")
            db.session.rollback()
            raise
    
    def _evaluate_rule_conditions(self, record, rule):
        """Evaluate rule conditions against a record"""
        try:
            if not rule.conditions:
                return False
            
            conditions = rule.conditions
            
            # Handle different condition structures
            if isinstance(conditions, dict):
                if 'logic' in conditions and 'conditions' in conditions:
                    # Complex condition with logic operator
                    return self._evaluate_complex_conditions(record, conditions)
                else:
                    # Simple single condition
                    return self._evaluate_single_condition(record, conditions)
            elif isinstance(conditions, list):
                # List of conditions (default AND logic)
                return all(self._evaluate_single_condition(record, cond) for cond in conditions)
            
            return False
            
        except Exception as e:
            logger.error(f"Error evaluating rule conditions for rule {rule.name}: {str(e)}")
            return False
    
    def _evaluate_complex_conditions(self, record, conditions):
        """Evaluate complex conditions with AND/OR logic"""
        logic = conditions.get('logic', 'AND').upper()
        condition_list = conditions.get('conditions', [])
        
        if not condition_list:
            return False
        
        results = []
        for condition in condition_list:
            if isinstance(condition, dict) and 'logic' in condition:
                # Nested complex condition
                result = self._evaluate_complex_conditions(record, condition)
            else:
                # Simple condition
                result = self._evaluate_single_condition(record, condition)
            results.append(result)
        
        if logic == 'OR':
            return any(results)
        else:  # Default to AND
            return all(results)
    
    def _evaluate_single_condition(self, record, condition):
        """Evaluate a single condition against a record"""
        try:
            field = condition.get('field')
            operator = condition.get('operator')
            value = condition.get('value', '')
            case_sensitive = condition.get('case_sensitive', False)
            
            if field not in self.supported_fields:
                logger.warning(f"Unsupported field: {field}")
                return False
            
            if operator not in self.supported_operators:
                logger.warning(f"Unsupported operator: {operator}")
                return False
            
            # Get field value from record
            record_value = getattr(record, field, '')
            if record_value is None:
                record_value = ''
            
            # Convert to string for comparison
            record_value = str(record_value)
            value = str(value)
            
            # Apply case sensitivity
            if not case_sensitive:
                record_value = record_value.lower()
                value = value.lower()
            
            # Evaluate based on operator
            return self._apply_operator(record_value, operator, value)
            
        except Exception as e:
            logger.error(f"Error evaluating single condition: {str(e)}")
            return False
    
    def _apply_operator(self, record_value, operator, value):
        """Apply the specified operator to compare values"""
        try:
            if operator == 'equals':
                return record_value == value
            
            elif operator == 'not_equals':
                return record_value != value
            
            elif operator == 'contains':
                return value in record_value
            
            elif operator == 'not_contains':
                return value not in record_value
            
            elif operator == 'starts_with':
                return record_value.startswith(value)
            
            elif operator == 'ends_with':
                return record_value.endswith(value)
            
            elif operator == 'in_list':
                # Value should be a comma-separated list
                value_list = [v.strip() for v in value.split(',')]
                return record_value in value_list
            
            elif operator == 'not_in_list':
                value_list = [v.strip() for v in value.split(',')]
                return record_value not in value_list
            
            elif operator == 'greater_than':
                try:
                    return float(record_value) > float(value)
                except ValueError:
                    return len(record_value) > len(value)
            
            elif operator == 'less_than':
                try:
                    return float(record_value) < float(value)
                except ValueError:
                    return len(record_value) < len(value)
            
            elif operator == 'matches_pattern':
                # Regular expression matching
                try:
                    return bool(re.search(value, record_value))
                except re.error:
                    logger.error(f"Invalid regex pattern: {value}")
                    return False
            
            elif operator == 'is_empty':
                return not record_value or record_value.strip() == ''
            
            elif operator == 'is_not_empty':
                return bool(record_value and record_value.strip())
            
            else:
                logger.warning(f"Unknown operator: {operator}")
                return False
                
        except Exception as e:
            logger.error(f"Error applying operator {operator}: {str(e)}")
            return False
    
    def _apply_rule_actions(self, record, rule):
        """Apply rule actions to a record"""
        try:
            if not rule.actions:
                return
            
            actions = rule.actions
            
            if actions.get('escalate'):
                record.case_status = 'Escalated'
                record.escalated_at = datetime.utcnow()
            
            if actions.get('flag'):
                # Add flag to notes
                flag_message = actions.get('flag_message', f'Flagged by rule: {rule.name}')
                if record.notes:
                    record.notes += f'\n{flag_message}'
                else:
                    record.notes = flag_message
            
            if actions.get('score_modifier'):
                # Modify risk score
                modifier = float(actions.get('score_modifier', 0))
                if record.ml_risk_score is not None:
                    record.ml_risk_score = min(max(record.ml_risk_score + modifier, 0), 1)
                else:
                    record.ml_risk_score = max(modifier, 0)
            
            if actions.get('tag'):
                # Add tag to record
                tag = actions.get('tag')
                if record.notes:
                    record.notes += f'\nTag: {tag}'
                else:
                    record.notes = f'Tag: {tag}'
            
            if actions.get('assign_to'):
                record.assigned_to = actions.get('assign_to')
                
        except Exception as e:
            logger.error(f"Error applying rule actions: {str(e)}")
    
    def test_rule(self, rule_data, test_records):
        """Test a rule against sample records"""
        try:
            # Create temporary rule object
            temp_rule = Rule(
                name=rule_data.get('name', 'Test Rule'),
                conditions=rule_data.get('conditions'),
                actions=rule_data.get('actions', {})
            )
            
            matches = []
            for record in test_records:
                if self._evaluate_rule_conditions(record, temp_rule):
                    matches.append({
                        'record_id': record.record_id,
                        'sender': record.sender,
                        'subject': record.subject[:100],  # Truncate for display
                        'recipients_email_domain': record.recipients_email_domain
                    })
            
            return {
                'matches': matches,
                'match_count': len(matches),
                'total_tested': len(test_records),
                'match_percentage': (len(matches) / len(test_records) * 100) if test_records else 0
            }
            
        except Exception as e:
            logger.error(f"Error testing rule: {str(e)}")
            return {'error': str(e)}
    
    def get_rule_impact_preview(self, rule_id, session_id=None):
        """Preview the impact of applying a rule"""
        try:
            rule = Rule.query.get(rule_id)
            if not rule:
                return {'error': 'Rule not found'}
            
            # Get records to test against
            if session_id:
                records = EmailRecord.query.filter_by(session_id=session_id).all()
            else:
                # Get sample records from recent sessions
                records = EmailRecord.query.limit(1000).all()
            
            impact = self.test_rule({
                'name': rule.name,
                'conditions': rule.conditions,
                'actions': rule.actions
            }, records)
            
            return impact
            
        except Exception as e:
            logger.error(f"Error getting rule impact preview: {str(e)}")
            return {'error': str(e)}
    
    def validate_rule_conditions(self, conditions):
        """Validate rule conditions structure and syntax"""
        try:
            validation_errors = []
            
            if not conditions:
                validation_errors.append("Conditions cannot be empty")
                return validation_errors
            
            if isinstance(conditions, dict):
                if 'logic' in conditions and 'conditions' in conditions:
                    # Complex condition structure
                    if conditions['logic'] not in ['AND', 'OR']:
                        validation_errors.append("Logic must be 'AND' or 'OR'")
                    
                    for i, condition in enumerate(conditions.get('conditions', [])):
                        errors = self._validate_single_condition(condition, f"Condition {i+1}")
                        validation_errors.extend(errors)
                else:
                    # Simple condition structure
                    errors = self._validate_single_condition(conditions, "Condition")
                    validation_errors.extend(errors)
            
            elif isinstance(conditions, list):
                for i, condition in enumerate(conditions):
                    errors = self._validate_single_condition(condition, f"Condition {i+1}")
                    validation_errors.extend(errors)
            
            else:
                validation_errors.append("Invalid conditions format")
            
            return validation_errors
            
        except Exception as e:
            return [f"Validation error: {str(e)}"]
    
    def _validate_single_condition(self, condition, prefix=""):
        """Validate a single condition"""
        errors = []
        
        if not isinstance(condition, dict):
            errors.append(f"{prefix}: Condition must be a dictionary")
            return errors
        
        # Check required fields
        if 'field' not in condition:
            errors.append(f"{prefix}: Missing 'field'")
        elif condition['field'] not in self.supported_fields:
            errors.append(f"{prefix}: Unsupported field '{condition['field']}'")
        
        if 'operator' not in condition:
            errors.append(f"{prefix}: Missing 'operator'")
        elif condition['operator'] not in self.supported_operators:
            errors.append(f"{prefix}: Unsupported operator '{condition['operator']}'")
        
        # Value is optional for some operators
        if condition.get('operator') in ['is_empty', 'is_not_empty']:
            # These operators don't need a value
            pass
        elif 'value' not in condition:
            errors.append(f"{prefix}: Missing 'value'")
        
        # Validate regex patterns
        if condition.get('operator') == 'matches_pattern':
            try:
                re.compile(condition.get('value', ''))
            except re.error as e:
                errors.append(f"{prefix}: Invalid regex pattern - {str(e)}")
        
        return errors
    
    def export_rules(self, rule_type=None):
        """Export rules to JSON format"""
        try:
            query = Rule.query.filter_by(is_active=True)
            if rule_type:
                query = query.filter_by(rule_type=rule_type)
            
            rules = query.all()
            
            exported_rules = []
            for rule in rules:
                exported_rules.append({
                    'name': rule.name,
                    'description': rule.description,
                    'rule_type': rule.rule_type,
                    'conditions': rule.conditions,
                    'actions': rule.actions,
                    'priority': rule.priority,
                    'created_at': rule.created_at.isoformat() if rule.created_at else None
                })
            
            return exported_rules
            
        except Exception as e:
            logger.error(f"Error exporting rules: {str(e)}")
            return []
    
    def import_rules(self, rules_data):
        """Import rules from JSON data"""
        try:
            imported_count = 0
            errors = []
            
            for rule_data in rules_data:
                try:
                    # Validate rule data
                    validation_errors = self.validate_rule_conditions(rule_data.get('conditions'))
                    if validation_errors:
                        errors.append(f"Rule '{rule_data.get('name')}': {', '.join(validation_errors)}")
                        continue
                    
                    # Check if rule already exists
                    existing_rule = Rule.query.filter_by(name=rule_data['name']).first()
                    if existing_rule:
                        errors.append(f"Rule '{rule_data['name']}' already exists")
                        continue
                    
                    # Create new rule
                    rule = Rule(
                        name=rule_data['name'],
                        description=rule_data.get('description', ''),
                        rule_type=rule_data.get('rule_type', 'security'),
                        conditions=rule_data['conditions'],
                        actions=rule_data.get('actions', {}),
                        priority=rule_data.get('priority', 1)
                    )
                    
                    db.session.add(rule)
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Error importing rule '{rule_data.get('name', 'Unknown')}': {str(e)}")
            
            if imported_count > 0:
                db.session.commit()
            
            return {
                'imported_count': imported_count,
                'errors': errors
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error importing rules: {str(e)}")
            return {
                'imported_count': 0,
                'errors': [f"Import failed: {str(e)}"]
            }
