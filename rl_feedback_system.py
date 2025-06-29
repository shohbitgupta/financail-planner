"""
Reinforcement Learning Feedback System for Financial Planner AI Agent
Implements RLHF (Reinforcement Learning from Human Feedback) to improve responses
"""

import os
import json
import logging
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

@dataclass
class UserFeedback:
    """User feedback data structure"""
    feedback_id: str
    user_id: str
    session_id: str
    query: str
    response: str
    rating: int  # 1-5 scale
    feedback_text: Optional[str]
    feedback_categories: List[str]  # ['accuracy', 'relevance', 'clarity', 'completeness']
    timestamp: str
    user_profile: Dict[str, Any]
    response_metadata: Dict[str, Any]

@dataclass
class ResponseQuality:
    """Response quality metrics"""
    overall_score: float
    accuracy_score: float
    relevance_score: float
    clarity_score: float
    completeness_score: float
    user_satisfaction: float
    improvement_suggestions: List[str]

class FeedbackDatabase:
    """Database for storing and managing feedback data"""
    
    def __init__(self, db_path: str = "feedback_database.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize feedback database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create feedback table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_feedback (
                    feedback_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    query TEXT NOT NULL,
                    response TEXT NOT NULL,
                    rating INTEGER NOT NULL,
                    feedback_text TEXT,
                    feedback_categories TEXT,
                    timestamp TEXT NOT NULL,
                    user_profile TEXT NOT NULL,
                    response_metadata TEXT NOT NULL
                )
            ''')
            
            # Create response quality table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS response_quality (
                    quality_id TEXT PRIMARY KEY,
                    feedback_id TEXT NOT NULL,
                    overall_score REAL NOT NULL,
                    accuracy_score REAL NOT NULL,
                    relevance_score REAL NOT NULL,
                    clarity_score REAL NOT NULL,
                    completeness_score REAL NOT NULL,
                    user_satisfaction REAL NOT NULL,
                    improvement_suggestions TEXT,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (feedback_id) REFERENCES user_feedback (feedback_id)
                )
            ''')
            
            # Create learning patterns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_patterns (
                    pattern_id TEXT PRIMARY KEY,
                    pattern_type TEXT NOT NULL,
                    pattern_data TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    usage_count INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0.0,
                    last_updated TEXT NOT NULL
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Feedback database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize feedback database: {str(e)}")
    
    def store_feedback(self, feedback: UserFeedback) -> bool:
        """Store user feedback in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_feedback 
                (feedback_id, user_id, session_id, query, response, rating, 
                 feedback_text, feedback_categories, timestamp, user_profile, response_metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                feedback.feedback_id,
                feedback.user_id,
                feedback.session_id,
                feedback.query,
                feedback.response,
                feedback.rating,
                feedback.feedback_text,
                json.dumps(feedback.feedback_categories),
                feedback.timestamp,
                json.dumps(feedback.user_profile),
                json.dumps(feedback.response_metadata)
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Failed to store feedback: {str(e)}")
            return False
    
    def get_feedback_by_criteria(self, criteria: Dict[str, Any]) -> List[UserFeedback]:
        """Retrieve feedback based on criteria"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build dynamic query
            where_clauses = []
            params = []
            
            for key, value in criteria.items():
                if key in ['user_id', 'session_id', 'rating']:
                    where_clauses.append(f"{key} = ?")
                    params.append(value)
                elif key == 'min_rating':
                    where_clauses.append("rating >= ?")
                    params.append(value)
                elif key == 'date_range':
                    where_clauses.append("timestamp BETWEEN ? AND ?")
                    params.extend(value)
            
            where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
            
            cursor.execute(f'''
                SELECT * FROM user_feedback WHERE {where_clause}
                ORDER BY timestamp DESC
            ''', params)
            
            rows = cursor.fetchall()
            conn.close()
            
            # Convert to UserFeedback objects
            feedback_list = []
            for row in rows:
                feedback = UserFeedback(
                    feedback_id=row[0],
                    user_id=row[1],
                    session_id=row[2],
                    query=row[3],
                    response=row[4],
                    rating=row[5],
                    feedback_text=row[6],
                    feedback_categories=json.loads(row[7]) if row[7] else [],
                    timestamp=row[8],
                    user_profile=json.loads(row[9]),
                    response_metadata=json.loads(row[10])
                )
                feedback_list.append(feedback)
            
            return feedback_list
            
        except Exception as e:
            logger.error(f"Failed to retrieve feedback: {str(e)}")
            return []

class ReinforcementLearningEngine:
    """
    Reinforcement Learning engine for improving financial planning responses
    """
    
    def __init__(self, feedback_db: FeedbackDatabase):
        self.feedback_db = feedback_db
        self.learning_patterns = defaultdict(list)
        self.response_templates = {}
        self.quality_thresholds = {
            'excellent': 4.5,
            'good': 3.5,
            'acceptable': 2.5,
            'poor': 1.5
        }
        self.load_learning_patterns()
    
    def load_learning_patterns(self):
        """Load existing learning patterns from database"""
        try:
            conn = sqlite3.connect(self.feedback_db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM learning_patterns')
            rows = cursor.fetchall()
            conn.close()
            
            for row in rows:
                pattern_type = row[1]
                pattern_data = json.loads(row[2])
                confidence_score = row[3]
                
                self.learning_patterns[pattern_type].append({
                    'pattern_id': row[0],
                    'data': pattern_data,
                    'confidence': confidence_score,
                    'usage_count': row[4],
                    'success_rate': row[5],
                    'last_updated': row[6]
                })
            
            logger.info(f"Loaded {len(rows)} learning patterns")
            
        except Exception as e:
            logger.error(f"Failed to load learning patterns: {str(e)}")
    
    def analyze_feedback_patterns(self) -> Dict[str, Any]:
        """Analyze feedback patterns to identify improvement opportunities"""
        try:
            # Get recent feedback (last 30 days)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            criteria = {
                'date_range': [start_date.isoformat(), end_date.isoformat()]
            }
            
            feedback_list = self.feedback_db.get_feedback_by_criteria(criteria)
            
            if not feedback_list:
                return {'message': 'No recent feedback available for analysis'}
            
            # Analyze patterns
            analysis = {
                'total_feedback': len(feedback_list),
                'average_rating': np.mean([f.rating for f in feedback_list]),
                'rating_distribution': self._calculate_rating_distribution(feedback_list),
                'common_issues': self._identify_common_issues(feedback_list),
                'successful_patterns': self._identify_successful_patterns(feedback_list),
                'improvement_recommendations': self._generate_improvement_recommendations(feedback_list)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze feedback patterns: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_rating_distribution(self, feedback_list: List[UserFeedback]) -> Dict[int, int]:
        """Calculate distribution of ratings"""
        distribution = defaultdict(int)
        for feedback in feedback_list:
            distribution[feedback.rating] += 1
        return dict(distribution)
    
    def _identify_common_issues(self, feedback_list: List[UserFeedback]) -> List[Dict[str, Any]]:
        """Identify common issues from low-rated feedback"""
        low_rated_feedback = [f for f in feedback_list if f.rating <= 2]
        
        issue_patterns = defaultdict(int)
        issue_examples = defaultdict(list)
        
        for feedback in low_rated_feedback:
            if feedback.feedback_text:
                # Simple keyword-based issue identification
                text = feedback.feedback_text.lower()
                
                if any(word in text for word in ['inaccurate', 'wrong', 'incorrect']):
                    issue_patterns['accuracy'] += 1
                    issue_examples['accuracy'].append(feedback.feedback_text[:100])
                
                if any(word in text for word in ['irrelevant', 'not helpful', 'off-topic']):
                    issue_patterns['relevance'] += 1
                    issue_examples['relevance'].append(feedback.feedback_text[:100])
                
                if any(word in text for word in ['unclear', 'confusing', 'hard to understand']):
                    issue_patterns['clarity'] += 1
                    issue_examples['clarity'].append(feedback.feedback_text[:100])
                
                if any(word in text for word in ['incomplete', 'missing', 'not enough']):
                    issue_patterns['completeness'] += 1
                    issue_examples['completeness'].append(feedback.feedback_text[:100])
        
        # Convert to list of issues sorted by frequency
        issues = []
        for issue_type, count in sorted(issue_patterns.items(), key=lambda x: x[1], reverse=True):
            issues.append({
                'type': issue_type,
                'frequency': count,
                'examples': issue_examples[issue_type][:3]  # Top 3 examples
            })
        
        return issues
    
    def _identify_successful_patterns(self, feedback_list: List[UserFeedback]) -> List[Dict[str, Any]]:
        """Identify patterns from high-rated feedback"""
        high_rated_feedback = [f for f in feedback_list if f.rating >= 4]
        
        success_patterns = []
        
        # Analyze user profile patterns for successful responses
        profile_patterns = defaultdict(list)
        for feedback in high_rated_feedback:
            profile = feedback.user_profile
            key = f"{profile.get('risk_tolerance', 'unknown')}_{profile.get('preferred_market', 'unknown')}"
            profile_patterns[key].append(feedback)
        
        for pattern_key, pattern_feedback in profile_patterns.items():
            if len(pattern_feedback) >= 3:  # At least 3 successful cases
                success_patterns.append({
                    'type': 'user_profile_pattern',
                    'pattern': pattern_key,
                    'success_count': len(pattern_feedback),
                    'average_rating': np.mean([f.rating for f in pattern_feedback]),
                    'common_elements': self._extract_common_response_elements(pattern_feedback)
                })
        
        return success_patterns
    
    def _extract_common_response_elements(self, feedback_list: List[UserFeedback]) -> List[str]:
        """Extract common elements from successful responses"""
        # This is a simplified implementation
        # In practice, you'd use NLP techniques to identify common patterns
        common_elements = []
        
        # Check for common response structures
        responses = [f.response for f in feedback_list]
        
        if all('Goal Achievement Timeline' in response for response in responses):
            common_elements.append('Includes clear goal timeline')
        
        if all('Monthly Savings' in response for response in responses):
            common_elements.append('Provides specific savings amounts')
        
        if all('Risk Assessment' in response for response in responses):
            common_elements.append('Includes risk assessment')
        
        return common_elements
    
    def _generate_improvement_recommendations(self, feedback_list: List[UserFeedback]) -> List[str]:
        """Generate specific improvement recommendations"""
        recommendations = []
        
        # Calculate average rating by category
        category_ratings = defaultdict(list)
        for feedback in feedback_list:
            for category in feedback.feedback_categories:
                category_ratings[category].append(feedback.rating)
        
        # Generate recommendations based on low-performing categories
        for category, ratings in category_ratings.items():
            avg_rating = np.mean(ratings)
            if avg_rating < 3.0:
                if category == 'accuracy':
                    recommendations.append("Improve data accuracy by updating financial instruments database")
                elif category == 'relevance':
                    recommendations.append("Enhance context retrieval to provide more relevant recommendations")
                elif category == 'clarity':
                    recommendations.append("Simplify language and improve response structure")
                elif category == 'completeness':
                    recommendations.append("Ensure all user goals are addressed in recommendations")
        
        # Add general recommendations
        avg_overall_rating = np.mean([f.rating for f in feedback_list])
        if avg_overall_rating < 3.5:
            recommendations.append("Consider implementing more personalized recommendation algorithms")
            recommendations.append("Add more detailed explanations for investment recommendations")
        
        return recommendations
    
    def update_response_strategy(self, user_profile: Dict[str, Any], 
                               feedback_history: List[UserFeedback]) -> Dict[str, Any]:
        """
        Update response strategy based on user's feedback history
        """
        try:
            if not feedback_history:
                return {'strategy': 'default', 'confidence': 0.5}
            
            # Analyze user's feedback patterns
            avg_rating = np.mean([f.rating for f in feedback_history])
            recent_feedback = sorted(feedback_history, key=lambda x: x.timestamp, reverse=True)[:5]
            
            strategy = {
                'personalization_level': 'high' if avg_rating >= 4.0 else 'medium',
                'detail_level': 'comprehensive' if any('incomplete' in (f.feedback_text or '') for f in recent_feedback) else 'standard',
                'explanation_style': 'technical' if user_profile.get('financial_knowledge', 'basic') == 'advanced' else 'simple',
                'focus_areas': self._determine_focus_areas(recent_feedback),
                'confidence': min(len(feedback_history) / 10.0, 1.0)  # Confidence based on feedback volume
            }
            
            return strategy
            
        except Exception as e:
            logger.error(f"Failed to update response strategy: {str(e)}")
            return {'strategy': 'default', 'confidence': 0.5}
    
    def _determine_focus_areas(self, recent_feedback: List[UserFeedback]) -> List[str]:
        """Determine areas to focus on based on recent feedback"""
        focus_areas = []
        
        # Analyze feedback categories that received low ratings
        low_rated_categories = []
        for feedback in recent_feedback:
            if feedback.rating <= 2:
                low_rated_categories.extend(feedback.feedback_categories)
        
        # Count frequency of low-rated categories
        category_counts = defaultdict(int)
        for category in low_rated_categories:
            category_counts[category] += 1
        
        # Focus on most problematic areas
        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            if count >= 2:  # If category appears in multiple low ratings
                focus_areas.append(category)
        
        return focus_areas[:3]  # Top 3 focus areas
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights from the learning system"""
        try:
            # Analyze recent patterns
            analysis = self.analyze_feedback_patterns()
            
            # Get system performance metrics
            all_feedback = self.feedback_db.get_feedback_by_criteria({})
            
            if not all_feedback:
                return {'message': 'No feedback data available'}
            
            insights = {
                'system_performance': {
                    'total_interactions': len(all_feedback),
                    'average_rating': np.mean([f.rating for f in all_feedback]),
                    'improvement_trend': self._calculate_improvement_trend(all_feedback),
                    'user_satisfaction_rate': len([f for f in all_feedback if f.rating >= 4]) / len(all_feedback)
                },
                'learning_effectiveness': {
                    'patterns_identified': len(self.learning_patterns),
                    'successful_adaptations': self._count_successful_adaptations(),
                    'areas_for_improvement': analysis.get('improvement_recommendations', [])
                },
                'recent_analysis': analysis
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to get learning insights: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_improvement_trend(self, feedback_list: List[UserFeedback]) -> str:
        """Calculate if the system is improving over time"""
        if len(feedback_list) < 10:
            return 'insufficient_data'
        
        # Sort by timestamp
        sorted_feedback = sorted(feedback_list, key=lambda x: x.timestamp)
        
        # Compare first half vs second half
        mid_point = len(sorted_feedback) // 2
        first_half_avg = np.mean([f.rating for f in sorted_feedback[:mid_point]])
        second_half_avg = np.mean([f.rating for f in sorted_feedback[mid_point:]])
        
        if second_half_avg > first_half_avg + 0.2:
            return 'improving'
        elif second_half_avg < first_half_avg - 0.2:
            return 'declining'
        else:
            return 'stable'
    
    def _count_successful_adaptations(self) -> int:
        """Count successful adaptations based on learning patterns"""
        successful_adaptations = 0
        for pattern_type, patterns in self.learning_patterns.items():
            for pattern in patterns:
                if pattern['success_rate'] > 0.7 and pattern['usage_count'] > 5:
                    successful_adaptations += 1
        return successful_adaptations

# Global instances
feedback_db = FeedbackDatabase()
rl_engine = ReinforcementLearningEngine(feedback_db)

def collect_user_feedback(feedback_data: Dict[str, Any]) -> bool:
    """Collect and store user feedback"""
    try:
        feedback = UserFeedback(
            feedback_id=feedback_data['feedback_id'],
            user_id=feedback_data['user_id'],
            session_id=feedback_data['session_id'],
            query=feedback_data['query'],
            response=feedback_data['response'],
            rating=feedback_data['rating'],
            feedback_text=feedback_data.get('feedback_text'),
            feedback_categories=feedback_data.get('feedback_categories', []),
            timestamp=feedback_data.get('timestamp', datetime.now().isoformat()),
            user_profile=feedback_data['user_profile'],
            response_metadata=feedback_data.get('response_metadata', {})
        )
        
        return feedback_db.store_feedback(feedback)
        
    except Exception as e:
        logger.error(f"Failed to collect user feedback: {str(e)}")
        return False

def get_adaptive_response_strategy(user_profile: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """Get adaptive response strategy based on user's feedback history"""
    try:
        # Get user's feedback history
        feedback_history = feedback_db.get_feedback_by_criteria({'user_id': user_id})
        
        # Update response strategy
        strategy = rl_engine.update_response_strategy(user_profile, feedback_history)
        
        return strategy
        
    except Exception as e:
        logger.error(f"Failed to get adaptive response strategy: {str(e)}")
        return {'strategy': 'default', 'confidence': 0.5}
