"""
Reinforcement Learning Feedback System for Financial Planning AI
Collects user feedback and adapts response strategies
"""

import json
import sqlite3
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import numpy as np
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FeedbackData:
    """User feedback data structure"""
    feedback_id: str
    user_id: str
    session_id: str
    rating: int  # 1-5 scale
    feedback_text: str
    feedback_categories: List[str]
    query: str
    response: str
    user_profile: Dict[str, Any]
    timestamp: str
    response_strategy: Optional[Dict[str, Any]] = None

@dataclass
class ResponseStrategy:
    """Adaptive response strategy"""
    strategy: str  # 'conservative', 'balanced', 'aggressive', 'comprehensive'
    detail_level: str  # 'basic', 'detailed', 'comprehensive'
    focus_areas: List[str]  # ['risk_analysis', 'returns', 'diversification', 'platforms']
    confidence: float  # 0.0 to 1.0

class RLFeedbackEngine:
    """Reinforcement Learning engine for feedback processing"""
    
    def __init__(self, db_path: str = "flask_api/rl_feedback.db"):
        self.db_path = db_path
        self.initialize_database()
        
    def initialize_database(self):
        """Initialize SQLite database for feedback storage"""
        try:
            # Ensure directory exists
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create feedback table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    feedback_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    rating INTEGER NOT NULL,
                    feedback_text TEXT,
                    feedback_categories TEXT,
                    query TEXT NOT NULL,
                    response TEXT NOT NULL,
                    user_profile TEXT NOT NULL,
                    response_strategy TEXT,
                    timestamp TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create user patterns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_patterns (
                    user_id TEXT PRIMARY KEY,
                    preferred_strategy TEXT,
                    avg_rating REAL,
                    total_interactions INTEGER,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                    pattern_data TEXT
                )
            ''')
            
            # Create learning metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ RL feedback database initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
    
    def store_feedback(self, feedback: FeedbackData) -> bool:
        """Store user feedback in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO feedback (
                    feedback_id, user_id, session_id, rating, feedback_text,
                    feedback_categories, query, response, user_profile,
                    response_strategy, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                feedback.feedback_id,
                feedback.user_id,
                feedback.session_id,
                feedback.rating,
                feedback.feedback_text,
                json.dumps(feedback.feedback_categories),
                feedback.query,
                feedback.response,
                json.dumps(feedback.user_profile),
                json.dumps(feedback.response_strategy) if feedback.response_strategy else None,
                feedback.timestamp
            ))
            
            conn.commit()
            conn.close()
            
            # Update user patterns
            self._update_user_patterns(feedback)
            
            # Update learning metrics
            self._update_learning_metrics(feedback)
            
            logger.info(f"✅ Stored feedback: {feedback.feedback_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store feedback: {e}")
            return False
    
    def get_adaptive_strategy(self, user_profile: Dict[str, Any], user_id: str) -> ResponseStrategy:
        """Get adaptive response strategy based on user patterns and feedback"""
        try:
            # Get user patterns
            user_patterns = self._get_user_patterns(user_id)
            
            # Analyze user profile
            risk_tolerance = user_profile.get('risk_tolerance', 'moderate').lower()
            age = user_profile.get('age', 35)
            goals = user_profile.get('goals', [])
            
            # Determine base strategy
            if user_patterns and user_patterns.get('preferred_strategy'):
                base_strategy = user_patterns['preferred_strategy']
                confidence = min(0.9, user_patterns.get('avg_rating', 3.0) / 5.0 + 0.2)
            else:
                # Default strategy based on profile
                if risk_tolerance == 'conservative' or age > 50:
                    base_strategy = 'conservative'
                elif risk_tolerance == 'aggressive' and age < 40:
                    base_strategy = 'aggressive'
                else:
                    base_strategy = 'balanced'
                confidence = 0.5
            
            # Determine detail level
            if user_patterns and user_patterns.get('avg_rating', 0) >= 4.0:
                detail_level = 'comprehensive'
            elif user_patterns and user_patterns.get('avg_rating', 0) >= 3.0:
                detail_level = 'detailed'
            else:
                detail_level = 'basic'
            
            # Determine focus areas based on goals and feedback
            focus_areas = ['risk_analysis', 'returns']
            if 'retirement' in str(goals).lower():
                focus_areas.append('diversification')
            if user_patterns and 'platforms' in str(user_patterns.get('pattern_data', '')):
                focus_areas.append('platforms')
            
            return ResponseStrategy(
                strategy=base_strategy,
                detail_level=detail_level,
                focus_areas=focus_areas,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Failed to get adaptive strategy: {e}")
            return ResponseStrategy(
                strategy='balanced',
                detail_level='basic',
                focus_areas=['risk_analysis', 'returns'],
                confidence=0.5
            )
    
    def _get_user_patterns(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user patterns from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT preferred_strategy, avg_rating, total_interactions, pattern_data
                FROM user_patterns WHERE user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'preferred_strategy': result[0],
                    'avg_rating': result[1],
                    'total_interactions': result[2],
                    'pattern_data': json.loads(result[3]) if result[3] else {}
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user patterns: {e}")
            return None
    
    def _update_user_patterns(self, feedback: FeedbackData):
        """Update user patterns based on new feedback"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get current patterns
            cursor.execute('''
                SELECT avg_rating, total_interactions, pattern_data
                FROM user_patterns WHERE user_id = ?
            ''', (feedback.user_id,))
            
            result = cursor.fetchone()
            
            if result:
                # Update existing patterns
                current_avg = result[0]
                current_total = result[1]
                pattern_data = json.loads(result[2]) if result[2] else {}
                
                # Calculate new average
                new_total = current_total + 1
                new_avg = ((current_avg * current_total) + feedback.rating) / new_total
                
                # Update pattern data
                if feedback.rating >= 4:
                    pattern_data['high_rating_categories'] = pattern_data.get('high_rating_categories', []) + feedback.feedback_categories
                
                # Determine preferred strategy
                if feedback.rating >= 4 and feedback.response_strategy:
                    preferred_strategy = feedback.response_strategy.get('strategy', 'balanced')
                else:
                    preferred_strategy = pattern_data.get('preferred_strategy', 'balanced')
                
                cursor.execute('''
                    UPDATE user_patterns 
                    SET preferred_strategy = ?, avg_rating = ?, total_interactions = ?,
                        pattern_data = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (preferred_strategy, new_avg, new_total, json.dumps(pattern_data), feedback.user_id))
                
            else:
                # Create new patterns
                pattern_data = {
                    'first_interaction': feedback.timestamp,
                    'categories': feedback.feedback_categories
                }
                
                preferred_strategy = 'balanced'
                if feedback.response_strategy:
                    preferred_strategy = feedback.response_strategy.get('strategy', 'balanced')
                
                cursor.execute('''
                    INSERT INTO user_patterns (
                        user_id, preferred_strategy, avg_rating, total_interactions, pattern_data
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (feedback.user_id, preferred_strategy, feedback.rating, 1, json.dumps(pattern_data)))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to update user patterns: {e}")
    
    def _update_learning_metrics(self, feedback: FeedbackData):
        """Update learning metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Store rating metric
            cursor.execute('''
                INSERT INTO learning_metrics (metric_name, metric_value)
                VALUES (?, ?)
            ''', ('user_rating', feedback.rating))
            
            # Store category-specific metrics
            for category in feedback.feedback_categories:
                cursor.execute('''
                    INSERT INTO learning_metrics (metric_name, metric_value)
                    VALUES (?, ?)
                ''', (f'category_{category}', feedback.rating))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to update learning metrics: {e}")
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get learning insights and system performance metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # System performance metrics
            cursor.execute('SELECT COUNT(*), AVG(rating) FROM feedback')
            total_interactions, avg_rating = cursor.fetchone()
            
            # Satisfaction rate (ratings >= 4)
            cursor.execute('SELECT COUNT(*) FROM feedback WHERE rating >= 4')
            satisfied_users = cursor.fetchone()[0]
            satisfaction_rate = satisfied_users / total_interactions if total_interactions > 0 else 0
            
            # Recent trend (last 30 days vs previous 30 days)
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            sixty_days_ago = (datetime.now() - timedelta(days=60)).isoformat()
            
            cursor.execute('''
                SELECT AVG(rating) FROM feedback 
                WHERE timestamp >= ? AND timestamp < ?
            ''', (thirty_days_ago, datetime.now().isoformat()))
            recent_avg = cursor.fetchone()[0] or 0
            
            cursor.execute('''
                SELECT AVG(rating) FROM feedback 
                WHERE timestamp >= ? AND timestamp < ?
            ''', (sixty_days_ago, thirty_days_ago))
            previous_avg = cursor.fetchone()[0] or 0
            
            # Determine trend
            if recent_avg > previous_avg + 0.2:
                trend = 'improving'
            elif recent_avg < previous_avg - 0.2:
                trend = 'declining'
            else:
                trend = 'stable'
            
            # Learning effectiveness
            cursor.execute('SELECT COUNT(DISTINCT user_id) FROM user_patterns')
            patterns_identified = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM user_patterns WHERE avg_rating >= 4.0')
            successful_adaptations = cursor.fetchone()[0]
            
            # Areas for improvement
            cursor.execute('''
                SELECT feedback_categories, AVG(rating) 
                FROM feedback 
                GROUP BY feedback_categories 
                HAVING AVG(rating) < 3.5
            ''')
            low_rating_categories = cursor.fetchall()
            areas_for_improvement = [
                f"Improve {json.loads(cat)[0] if cat and cat != '[]' else 'general'} (avg: {avg:.1f})"
                for cat, avg in low_rating_categories
            ]
            
            conn.close()
            
            return {
                'system_performance': {
                    'total_interactions': total_interactions or 0,
                    'average_rating': avg_rating or 0,
                    'improvement_trend': trend,
                    'user_satisfaction_rate': satisfaction_rate
                },
                'learning_effectiveness': {
                    'patterns_identified': patterns_identified or 0,
                    'successful_adaptations': successful_adaptations or 0,
                    'areas_for_improvement': areas_for_improvement[:3]  # Top 3
                },
                'recent_analysis': {
                    'recent_avg_rating': recent_avg,
                    'previous_avg_rating': previous_avg,
                    'trend_direction': trend
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get learning insights: {e}")
            return {
                'system_performance': {
                    'total_interactions': 0,
                    'average_rating': 0,
                    'improvement_trend': 'unknown',
                    'user_satisfaction_rate': 0
                },
                'learning_effectiveness': {
                    'patterns_identified': 0,
                    'successful_adaptations': 0,
                    'areas_for_improvement': []
                },
                'recent_analysis': {
                    'recent_avg_rating': 0,
                    'previous_avg_rating': 0,
                    'trend_direction': 'unknown'
                }
            }

# Global RL engine instance
rl_engine = RLFeedbackEngine()

def collect_user_feedback(feedback_data: Dict[str, Any]) -> bool:
    """Collect user feedback for reinforcement learning"""
    try:
        feedback = FeedbackData(
            feedback_id=feedback_data['feedback_id'],
            user_id=feedback_data['user_id'],
            session_id=feedback_data['session_id'],
            rating=feedback_data['rating'],
            feedback_text=feedback_data.get('feedback_text', ''),
            feedback_categories=feedback_data.get('feedback_categories', []),
            query=feedback_data['query'],
            response=feedback_data['response'],
            user_profile=feedback_data['user_profile'],
            timestamp=feedback_data.get('timestamp', datetime.now().isoformat()),
            response_strategy=feedback_data.get('response_strategy')
        )
        
        return rl_engine.store_feedback(feedback)
        
    except Exception as e:
        logger.error(f"Failed to collect feedback: {e}")
        return False

def get_adaptive_response_strategy(user_profile: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """Get adaptive response strategy for user"""
    try:
        strategy = rl_engine.get_adaptive_strategy(user_profile, user_id)
        return asdict(strategy)
        
    except Exception as e:
        logger.error(f"Failed to get adaptive strategy: {e}")
        return {
            'strategy': 'balanced',
            'detail_level': 'basic',
            'focus_areas': ['risk_analysis', 'returns'],
            'confidence': 0.5
        }
