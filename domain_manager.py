import logging
import re
from collections import defaultdict, Counter
from datetime import datetime
from local_models import WhitelistDomain, EmailRecord, ProcessingSession
from local_app import db

logger = logging.getLogger(__name__)

class DomainManager:
    """Domain classification and whitelist management system"""
    
    def __init__(self):
        # Domain classification patterns
        self.domain_patterns = {
            'corporate': [
                r'\.com$', r'\.corp$', r'\.org$', r'\.gov$', r'\.edu$'
            ],
            'personal': [
                r'gmail\.com$', r'yahoo\.com$', r'hotmail\.com$', r'outlook\.com$',
                r'aol\.com$', r'icloud\.com$', r'protonmail\.com$'
            ],
            'public': [
                r'gmail\.com$', r'yahoo\.com$', r'hotmail\.com$', r'outlook\.com$',
                r'live\.com$', r'msn\.com$', r'ymail\.com$'
            ],
            'suspicious': [
                r'\.tk$', r'\.ml$', r'\.ga$', r'\.cf$', r'temp.*\.com$',
                r'10minutemail\.', r'guerrillamail\.', r'mailinator\.'
            ]
        }
        
        # Trust scoring weights
        self.trust_weights = {
            'communication_frequency': 0.3,
            'risk_score_avg': 0.4,
            'business_context': 0.2,
            'domain_reputation': 0.1
        }
    
    def apply_whitelist_filtering(self, session_id):
        """Apply whitelist filtering to session records"""
        try:
            logger.info(f"Applying whitelist filtering for session {session_id}")
            
            # Get active whitelist domains
            whitelist_domains = WhitelistDomain.query.filter_by(is_active=True).all()
            whitelist_set = set(domain.domain.lower() for domain in whitelist_domains)
            
            if not whitelist_set:
                logger.info("No whitelist domains found")
                return 0
            
            # Get non-excluded records
            records = EmailRecord.query.filter(
                EmailRecord.session_id == session_id,
                EmailRecord.excluded_by_rule.is_(None)
            ).all()
            
            whitelisted_count = 0
            
            for record in records:
                if record.recipients_email_domain:
                    domain = record.recipients_email_domain.lower()
                    if domain in whitelist_set:
                        record.whitelisted = True
                        whitelisted_count += 1
                        logger.debug(f"Record {record.record_id} whitelisted for domain: {domain}")
            
            db.session.commit()
            logger.info(f"Whitelist filtering applied: {whitelisted_count} records whitelisted")
            return whitelisted_count
            
        except Exception as e:
            logger.error(f"Error applying whitelist filtering: {str(e)}")
            db.session.rollback()
            raise
    
    def classify_domain(self, domain):
        """Classify a domain into categories"""
        if not domain:
            return 'Unknown'
        
        domain_lower = domain.lower()
        
        # Check against patterns
        for category, patterns in self.domain_patterns.items():
            for pattern in patterns:
                if re.search(pattern, domain_lower):
                    return category.title()
        
        # Default classification logic
        if any(corp in domain_lower for corp in ['company', 'corp', 'enterprise', 'business']):
            return 'Corporate'
        elif len(domain_lower.split('.')) == 2 and not domain_lower.endswith(('.com', '.org', '.net')):
            return 'Suspicious'
        else:
            return 'Corporate'
    
    def calculate_domain_trust_score(self, domain, session_records=None):
        """Calculate trust score for a domain (0-100)"""
        try:
            if not domain:
                return 0
            
            score_components = {
                'base_score': 50,  # Start with neutral score
                'frequency_bonus': 0,
                'risk_penalty': 0,
                'business_bonus': 0,
                'reputation_modifier': 0
            }
            
            # Get records for this domain
            if session_records:
                domain_records = [r for r in session_records 
                                if r.recipients_email_domain and r.recipients_email_domain.lower() == domain.lower()]
            else:
                domain_records = EmailRecord.query.filter(
                    db.func.lower(EmailRecord.recipients_email_domain) == domain.lower()
                ).all()
            
            if not domain_records:
                return score_components['base_score']
            
            # Communication frequency bonus (more communications = more trust)
            frequency_count = len(domain_records)
            if frequency_count > 10:
                score_components['frequency_bonus'] = min(20, frequency_count)
            elif frequency_count > 5:
                score_components['frequency_bonus'] = 10
            elif frequency_count > 2:
                score_components['frequency_bonus'] = 5
            
            # Risk score penalty
            risk_scores = [r.ml_risk_score for r in domain_records if r.ml_risk_score is not None]
            if risk_scores:
                avg_risk = sum(risk_scores) / len(risk_scores)
                score_components['risk_penalty'] = -int(avg_risk * 40)  # Higher risk = lower trust
            
            # Business context bonus
            business_indicators = ['business', 'corporate', 'official', 'legitimate']
            justifications = [r.justification or '' for r in domain_records]
            business_mentions = sum(1 for just in justifications 
                                  for indicator in business_indicators 
                                  if indicator in just.lower())
            
            if business_mentions > 0:
                score_components['business_bonus'] = min(15, business_mentions * 3)
            
            # Domain reputation modifier based on classification
            domain_class = self.classify_domain(domain)
            if domain_class == 'Corporate':
                score_components['reputation_modifier'] = 10
            elif domain_class == 'Personal':
                score_components['reputation_modifier'] = -5
            elif domain_class == 'Suspicious':
                score_components['reputation_modifier'] = -25
            
            # Calculate final score
            final_score = sum(score_components.values())
            final_score = max(0, min(100, final_score))  # Clamp between 0-100
            
            return int(final_score)
            
        except Exception as e:
            logger.error(f"Error calculating trust score for domain {domain}: {str(e)}")
            return 50  # Return neutral score on error
    
    def analyze_whitelist_recommendations(self, session_id):
        """Analyze and recommend domains for whitelisting"""
        try:
            logger.info(f"Analyzing whitelist recommendations for session {session_id}")
            
            # Get session records
            records = EmailRecord.query.filter_by(session_id=session_id).all()
            
            if not records:
                return {'error': 'No records found for session'}
            
            # Analyze domain patterns
            domain_stats = self._analyze_domain_communication_patterns(records)
            
            # Generate recommendations
            recommendations = self._generate_domain_recommendations(domain_stats, records)
            
            # Analyze current whitelist effectiveness
            whitelist_effectiveness = self._analyze_whitelist_effectiveness(session_id)
            
            # BAU pattern analysis
            bau_patterns = self._analyze_bau_communication_patterns(records)
            
            analysis = {
                'total_unique_domains': len(domain_stats),
                'domain_statistics': domain_stats,
                'whitelist_recommendations': recommendations,
                'whitelist_effectiveness': whitelist_effectiveness,
                'bau_patterns': bau_patterns,
                'summary': self._generate_whitelist_summary(domain_stats, recommendations)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing whitelist recommendations: {str(e)}")
            return {'error': str(e)}
    
    def _analyze_domain_communication_patterns(self, records):
        """Analyze communication patterns for each domain"""
        domain_stats = defaultdict(lambda: {
            'communication_count': 0,
            'unique_senders': set(),
            'risk_scores': [],
            'high_risk_count': 0,
            'justifications': [],
            'time_patterns': [],
            'attachment_count': 0,
            'classification': 'Unknown',
            'trust_score': 0
        })
        
        for record in records:
            if not record.recipients_email_domain:
                continue
            
            domain = record.recipients_email_domain.lower()
            stats = domain_stats[domain]
            
            stats['communication_count'] += 1
            if record.sender:
                stats['unique_senders'].add(record.sender.lower())
            
            if record.ml_risk_score is not None:
                stats['risk_scores'].append(record.ml_risk_score)
                if record.ml_risk_score > 0.6:
                    stats['high_risk_count'] += 1
            
            if record.justification:
                stats['justifications'].append(record.justification)
            
            if record.time:
                stats['time_patterns'].append(record.time)
            
            if record.attachments:
                stats['attachment_count'] += 1
        
        # Post-process statistics
        processed_stats = {}
        for domain, stats in domain_stats.items():
            stats['unique_senders'] = list(stats['unique_senders'])
            stats['avg_risk_score'] = sum(stats['risk_scores']) / len(stats['risk_scores']) if stats['risk_scores'] else 0
            stats['classification'] = self.classify_domain(domain)
            stats['trust_score'] = self.calculate_domain_trust_score(domain, records)
            stats['high_risk_ratio'] = stats['high_risk_count'] / stats['communication_count'] if stats['communication_count'] > 0 else 0
            
            processed_stats[domain] = dict(stats)
        
        return processed_stats
    
    def _generate_domain_recommendations(self, domain_stats, records):
        """Generate whitelist recommendations based on domain analysis"""
        recommendations = []
        
        # Get currently whitelisted domains
        current_whitelist = set(domain.domain.lower() for domain in 
                              WhitelistDomain.query.filter_by(is_active=True).all())
        
        # Sort domains by communication frequency and trust score
        sorted_domains = sorted(domain_stats.items(), 
                              key=lambda x: (x[1]['communication_count'], x[1]['trust_score']), 
                              reverse=True)
        
        for domain, stats in sorted_domains:
            if domain in current_whitelist:
                continue  # Skip already whitelisted domains
            
            # Criteria for recommendation
            should_recommend = (
                stats['communication_count'] >= 3 and  # Minimum communication threshold
                stats['avg_risk_score'] < 0.4 and      # Low average risk
                stats['high_risk_ratio'] < 0.2 and     # Low high-risk ratio
                stats['trust_score'] >= 60             # Good trust score
            )
            
            if should_recommend:
                confidence_level = 'High'
                if stats['trust_score'] < 70 or stats['avg_risk_score'] > 0.2:
                    confidence_level = 'Medium'
                elif stats['communication_count'] < 5:
                    confidence_level = 'Low'
                
                recommendation = {
                    'domain': domain,
                    'communication_count': stats['communication_count'],
                    'unique_senders': len(stats['unique_senders']),
                    'avg_risk_score': round(stats['avg_risk_score'], 3),
                    'high_risk_count': stats['high_risk_count'],
                    'trust_score': stats['trust_score'],
                    'classification': stats['classification'],
                    'confidence_level': confidence_level,
                    'recommendation_reason': self._generate_recommendation_reason(stats),
                    'potential_impact': self._calculate_whitelist_impact(domain, records)
                }
                
                recommendations.append(recommendation)
        
        return sorted(recommendations, key=lambda x: (x['trust_score'], x['communication_count']), reverse=True)
    
    def _generate_recommendation_reason(self, stats):
        """Generate human-readable reason for recommendation"""
        reasons = []
        
        if stats['communication_count'] >= 10:
            reasons.append(f"High volume communication ({stats['communication_count']} emails)")
        
        if stats['avg_risk_score'] < 0.2:
            reasons.append("Consistently low risk communications")
        
        if stats['trust_score'] >= 80:
            reasons.append("High trust score based on communication patterns")
        
        if len(stats['unique_senders']) > 1:
            reasons.append(f"Multiple senders ({len(stats['unique_senders'])}) indicate legitimate business relationship")
        
        if stats['classification'] == 'Corporate':
            reasons.append("Corporate domain classification")
        
        return "; ".join(reasons) if reasons else "Meets standard whitelist criteria"
    
    def _calculate_whitelist_impact(self, domain, records):
        """Calculate the potential impact of whitelisting a domain"""
        domain_records = [r for r in records 
                         if r.recipients_email_domain and r.recipients_email_domain.lower() == domain.lower()]
        
        total_records = len(records)
        domain_count = len(domain_records)
        
        return {
            'records_affected': domain_count,
            'percentage_of_total': round((domain_count / total_records * 100), 2) if total_records > 0 else 0,
            'processing_time_saved': f"~{domain_count * 0.1:.1f} seconds",  # Estimated
            'false_positive_reduction': domain_count
        }
    
    def _analyze_whitelist_effectiveness(self, session_id):
        """Analyze the effectiveness of current whitelist"""
        try:
            # Get whitelisted records
            whitelisted_records = EmailRecord.query.filter_by(
                session_id=session_id,
                whitelisted=True
            ).all()
            
            total_records = EmailRecord.query.filter_by(session_id=session_id).count()
            
            if not whitelisted_records:
                return {
                    'whitelisted_count': 0,
                    'effectiveness_score': 0,
                    'false_positive_reduction': 0,
                    'processing_efficiency_gain': 0
                }
            
            # Analyze whitelisted records
            avg_risk_of_whitelisted = 0
            high_risk_whitelisted = 0
            
            if whitelisted_records:
                risk_scores = [r.ml_risk_score for r in whitelisted_records if r.ml_risk_score is not None]
                if risk_scores:
                    avg_risk_of_whitelisted = sum(risk_scores) / len(risk_scores)
                    high_risk_whitelisted = sum(1 for score in risk_scores if score > 0.6)
            
            # Calculate effectiveness metrics
            whitelist_ratio = len(whitelisted_records) / total_records if total_records > 0 else 0
            effectiveness_score = max(0, 100 - (avg_risk_of_whitelisted * 100) - (high_risk_whitelisted * 10))
            
            return {
                'whitelisted_count': len(whitelisted_records),
                'whitelist_ratio': round(whitelist_ratio, 3),
                'avg_risk_of_whitelisted': round(avg_risk_of_whitelisted, 3),
                'high_risk_whitelisted': high_risk_whitelisted,
                'effectiveness_score': round(effectiveness_score, 1),
                'false_positive_reduction': len(whitelisted_records),
                'processing_efficiency_gain': round(whitelist_ratio * 100, 1)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing whitelist effectiveness: {str(e)}")
            return {'error': str(e)}
    
    def _analyze_bau_communication_patterns(self, records):
        """Analyze Business As Usual communication patterns"""
        bau_patterns = {
            'high_frequency_domains': [],
            'regular_communication_pairs': [],
            'business_hours_domains': [],
            'low_risk_high_volume': []
        }
        
        # Domain frequency analysis
        domain_frequency = Counter(r.recipients_email_domain.lower() 
                                 for r in records if r.recipients_email_domain)
        
        # High frequency domains (potential BAU)
        for domain, count in domain_frequency.most_common(10):
            if count >= 5:  # Threshold for high frequency
                domain_records = [r for r in records 
                                if r.recipients_email_domain and r.recipients_email_domain.lower() == domain]
                avg_risk = sum(r.ml_risk_score for r in domain_records if r.ml_risk_score) / len(domain_records)
                
                bau_patterns['high_frequency_domains'].append({
                    'domain': domain,
                    'frequency': count,
                    'avg_risk_score': round(avg_risk, 3) if avg_risk else 0,
                    'bau_likelihood': 'High' if avg_risk < 0.3 and count > 10 else 'Medium'
                })
        
        # Regular communication pairs (sender -> domain)
        sender_domain_pairs = defaultdict(int)
        for record in records:
            if record.sender and record.recipients_email_domain:
                sender_domain = self._extract_domain_from_email(record.sender)
                recipient_domain = record.recipients_email_domain.lower()
                pair = f"{sender_domain} -> {recipient_domain}"
                sender_domain_pairs[pair] += 1
        
        for pair, count in sender_domain_pairs.items():
            if count >= 3:  # Regular communication threshold
                bau_patterns['regular_communication_pairs'].append({
                    'pair': pair,
                    'frequency': count,
                    'bau_score': min(100, count * 10)  # Simple BAU scoring
                })
        
        return bau_patterns
    
    def _extract_domain_from_email(self, email):
        """Extract domain from email address"""
        if not email or '@' not in email:
            return 'unknown'
        return email.split('@')[-1].lower()
    
    def _generate_whitelist_summary(self, domain_stats, recommendations):
        """Generate summary of whitelist analysis"""
        total_domains = len(domain_stats)
        recommended_count = len(recommendations)
        high_confidence_count = len([r for r in recommendations if r['confidence_level'] == 'High'])
        
        # Calculate potential impact
        total_communications_affected = sum(r['communication_count'] for r in recommendations)
        
        return {
            'total_domains_analyzed': total_domains,
            'domains_recommended': recommended_count,
            'high_confidence_recommendations': high_confidence_count,
            'potential_communications_whitelisted': total_communications_affected,
            'whitelist_coverage_improvement': f"{recommended_count}/{total_domains} domains",
            'recommendation_summary': f"{recommended_count} domains recommended for whitelisting with {high_confidence_count} high-confidence recommendations"
        }
    
    def add_domain_to_whitelist(self, domain, domain_type='Corporate', added_by='System', notes=''):
        """Add a domain to the whitelist"""
        try:
            domain_lower = domain.lower()
            
            # Check if domain already exists
            existing = WhitelistDomain.query.filter_by(domain=domain_lower).first()
            if existing:
                if not existing.is_active:
                    existing.is_active = True
                    existing.added_at = datetime.utcnow()
                    existing.added_by = added_by
                    db.session.commit()
                    return {'status': 'reactivated', 'domain': domain_lower}
                else:
                    return {'status': 'already_exists', 'domain': domain_lower}
            
            # Add new domain
            whitelist_domain = WhitelistDomain(
                domain=domain_lower,
                domain_type=domain_type,
                added_by=added_by,
                notes=notes
            )
            
            db.session.add(whitelist_domain)
            db.session.commit()
            
            logger.info(f"Domain {domain_lower} added to whitelist by {added_by}")
            return {'status': 'added', 'domain': domain_lower}
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding domain to whitelist: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def remove_domain_from_whitelist(self, domain):
        """Remove a domain from the whitelist"""
        try:
            domain_lower = domain.lower()
            
            whitelist_domain = WhitelistDomain.query.filter_by(domain=domain_lower).first()
            if not whitelist_domain:
                return {'status': 'not_found', 'domain': domain_lower}
            
            whitelist_domain.is_active = False
            db.session.commit()
            
            logger.info(f"Domain {domain_lower} removed from whitelist")
            return {'status': 'removed', 'domain': domain_lower}
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error removing domain from whitelist: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def bulk_add_domains_to_whitelist(self, domains_list, added_by='Admin'):
        """Add multiple domains to whitelist in bulk"""
        try:
            results = {
                'added': [],
                'reactivated': [],
                'already_exists': [],
                'errors': []
            }
            
            for domain in domains_list:
                domain = domain.strip().lower()
                if not domain:
                    continue
                
                result = self.add_domain_to_whitelist(domain, added_by=added_by)
                status = result['status']
                
                if status in results:
                    results[status].append(domain)
                else:
                    results['errors'].append(f"{domain}: {result.get('error', 'Unknown error')}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in bulk domain addition: {str(e)}")
            return {'errors': [str(e)]}
