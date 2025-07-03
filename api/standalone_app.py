from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import re
import sys
import os
import uuid
import json
from datetime import datetime

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file"""
    env_file_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file_path):
        try:
            with open(env_file_path, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
            print(f"✅ Loaded environment variables from .env")
            return True
        except Exception as e:
            print(f"⚠️  Error loading .env file: {e}")
    return False

# Load environment variables
load_env_file()

# Import evaluator agent
try:
    from evaluator_agent import evaluate_and_improve_response
    EVALUATOR_AVAILABLE = True
    print("Evaluator agent loaded successfully")
except ImportError as e:
    print(f"Warning: Could not import evaluator agent: {e}")
    EVALUATOR_AVAILABLE = False

try:
    from investment_database import InvestmentDatabase
    DATABASE_AVAILABLE = True
    print("Investment database module loaded successfully")
except ImportError as e:
    print(f"Warning: Could not import investment database: {e}")
    DATABASE_AVAILABLE = False

# Import vector database retriever
try:
    from vectors import retriver
    VECTORS_AVAILABLE = True
    print("Vector database retriever loaded successfully")
except ImportError as e:
    print(f"Warning: Could not import vector database: {e}")
    VECTORS_AVAILABLE = False

# RL Feedback System Implementation
import sqlite3
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
import numpy as np

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

class RLFeedbackEngine:
    """Simple RL feedback engine for collecting and processing user feedback"""

    def __init__(self, db_path: str = "api/rl_feedback.db"):
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

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Failed to initialize RL database: {e}")

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
            return True

        except Exception as e:
            print(f"Failed to store feedback: {e}")
            return False

    def get_learning_insights(self) -> Dict[str, Any]:
        """Get learning insights and system performance metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # System performance metrics
            cursor.execute('SELECT COUNT(*), AVG(rating) FROM feedback')
            result = cursor.fetchone()
            total_interactions = result[0] if result[0] else 0
            avg_rating = result[1] if result[1] else 0

            # Satisfaction rate (ratings >= 4)
            cursor.execute('SELECT COUNT(*) FROM feedback WHERE rating >= 4')
            satisfied_result = cursor.fetchone()
            satisfied_users = satisfied_result[0] if satisfied_result else 0
            satisfaction_rate = satisfied_users / total_interactions if total_interactions > 0 else 0

            conn.close()

            return {
                'system_performance': {
                    'total_interactions': total_interactions,
                    'average_rating': round(avg_rating, 2),
                    'user_satisfaction_rate': round(satisfaction_rate, 2),
                    'improvement_trend': 'stable'
                },
                'learning_effectiveness': {
                    'patterns_identified': total_interactions,
                    'successful_adaptations': satisfied_users,
                    'areas_for_improvement': ['Continue collecting feedback']
                }
            }

        except Exception as e:
            print(f"Failed to get learning insights: {e}")
            return {
                'system_performance': {
                    'total_interactions': 0,
                    'average_rating': 0,
                    'user_satisfaction_rate': 0,
                    'improvement_trend': 'unknown'
                },
                'learning_effectiveness': {
                    'patterns_identified': 0,
                    'successful_adaptations': 0,
                    'areas_for_improvement': []
                }
            }

    def get_adaptive_response_strategy(self, user_profile: Dict[str, Any], user_id: str = None) -> Dict[str, Any]:
        """Generate adaptive response strategy based on historical feedback"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get feedback patterns for similar user profiles
            cursor.execute('''
                SELECT rating, feedback_text, feedback_categories, user_profile, query, response
                FROM feedback
                WHERE rating >= 4
                ORDER BY created_at DESC
                LIMIT 20
            ''')

            positive_feedback = cursor.fetchall()

            # Get negative feedback patterns
            cursor.execute('''
                SELECT rating, feedback_text, feedback_categories, user_profile, query, response
                FROM feedback
                WHERE rating <= 2
                ORDER BY created_at DESC
                LIMIT 10
            ''')

            negative_feedback = cursor.fetchall()

            conn.close()

            # Analyze patterns and generate strategy
            strategy = {
                'strategy_type': 'adaptive',
                'confidence': 0.7,
                'total_feedback_samples': len(positive_feedback) + len(negative_feedback),
                'positive_patterns': [],
                'areas_to_avoid': [],
                'recommended_focus': [],
                'prompt_adjustments': {}
            }

            # Extract positive patterns
            if positive_feedback:
                positive_categories = []
                for feedback in positive_feedback:
                    try:
                        categories = json.loads(feedback[2]) if feedback[2] else []
                        positive_categories.extend(categories)
                    except:
                        pass

                # Count most appreciated aspects
                from collections import Counter
                category_counts = Counter(positive_categories)
                strategy['positive_patterns'] = [
                    {'aspect': cat, 'frequency': count}
                    for cat, count in category_counts.most_common(5)
                ]

                # Generate recommendations based on positive feedback
                if 'accuracy' in [cat for cat, _ in category_counts.most_common(3)]:
                    strategy['recommended_focus'].append('Provide more specific numerical calculations')
                if 'relevance' in [cat for cat, _ in category_counts.most_common(3)]:
                    strategy['recommended_focus'].append('Focus on user-specific goals and constraints')
                if 'clarity' in [cat for cat, _ in category_counts.most_common(3)]:
                    strategy['recommended_focus'].append('Use clear, structured explanations')

            # Extract negative patterns to avoid
            if negative_feedback:
                negative_categories = []
                for feedback in negative_feedback:
                    try:
                        categories = json.loads(feedback[2]) if feedback[2] else []
                        negative_categories.extend(categories)
                    except:
                        pass

                from collections import Counter
                negative_counts = Counter(negative_categories)
                strategy['areas_to_avoid'] = [
                    {'issue': cat, 'frequency': count}
                    for cat, count in negative_counts.most_common(3)
                ]

            # Generate prompt adjustments based on patterns
            if strategy['positive_patterns']:
                top_positive = strategy['positive_patterns'][0]['aspect']
                if top_positive == 'accuracy':
                    strategy['prompt_adjustments']['emphasis'] = 'numerical_precision'
                elif top_positive == 'relevance':
                    strategy['prompt_adjustments']['emphasis'] = 'personalization'
                elif top_positive == 'clarity':
                    strategy['prompt_adjustments']['emphasis'] = 'structured_explanation'

            return strategy

        except Exception as e:
            print(f"Failed to generate adaptive strategy: {e}")
            return {
                'strategy_type': 'default',
                'confidence': 0.5,
                'total_feedback_samples': 0,
                'positive_patterns': [],
                'areas_to_avoid': [],
                'recommended_focus': [],
                'prompt_adjustments': {}
            }

# Initialize RL feedback system
try:
    rl_engine = RLFeedbackEngine()
    RL_FEEDBACK_AVAILABLE = True
    print("✅ RL feedback system available")
except Exception as e:
    print(f"⚠️ RL feedback system not available: {e}")
    RL_FEEDBACK_AVAILABLE = False
    rl_engine = None

def collect_user_feedback(feedback_data: Dict[str, Any]) -> bool:
    """Collect user feedback for reinforcement learning"""
    if not RL_FEEDBACK_AVAILABLE or not rl_engine:
        return False

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
        print(f"Failed to collect feedback: {e}")
        return False

def get_adaptive_response_strategy(user_profile: Dict[str, Any], user_id: str = None) -> Dict[str, Any]:
    """Get adaptive response strategy based on historical feedback"""
    if not RL_FEEDBACK_AVAILABLE or not rl_engine:
        return {
            'strategy_type': 'default',
            'confidence': 0.5,
            'recommended_focus': [],
            'prompt_adjustments': {}
        }

    return rl_engine.get_adaptive_response_strategy(user_profile, user_id)

def create_adaptive_prompt(base_prompt: str, strategy: Dict[str, Any], user_data: Dict[str, Any]) -> str:
    """Create an adaptive prompt based on feedback strategy"""

    # Start with base prompt
    adaptive_prompt = base_prompt

    # Add adaptive instructions based on strategy
    if strategy.get('recommended_focus'):
        focus_instructions = "\n\nBased on user feedback patterns, please pay special attention to:\n"
        for focus in strategy['recommended_focus']:
            focus_instructions += f"- {focus}\n"
        adaptive_prompt += focus_instructions

    # Add emphasis based on prompt adjustments
    emphasis = strategy.get('prompt_adjustments', {}).get('emphasis')
    if emphasis == 'numerical_precision':
        adaptive_prompt += "\n\nIMPORTANT: Provide precise numerical calculations and specific dollar amounts. Users value accuracy in financial projections."
    elif emphasis == 'personalization':
        adaptive_prompt += f"\n\nIMPORTANT: Tailor recommendations specifically to this user's profile: {user_data.get('age', 'N/A')} years old, {user_data.get('risk_tolerance', 'moderate')} risk tolerance, goals: {', '.join(user_data.get('goals', []))}."
    elif emphasis == 'structured_explanation':
        adaptive_prompt += "\n\nIMPORTANT: Use clear, well-structured explanations with bullet points and organized sections. Users prefer clarity and easy-to-follow recommendations."

    # Add areas to avoid based on negative feedback
    if strategy.get('areas_to_avoid'):
        avoid_instructions = "\n\nBased on user feedback, please avoid:\n"
        for area in strategy['areas_to_avoid']:
            avoid_instructions += f"- Issues related to {area['issue']} (mentioned {area['frequency']} times in negative feedback)\n"
        adaptive_prompt += avoid_instructions

    return adaptive_prompt

def get_wio_platform_recommendation(category, market):
    """Get WIO Bank platform recommendation based on investment category and market."""

    # WIO Invest App for Stocks
    if category.lower() in ['bond', 'equity', 'stock', 'etf'] or 'stock' in category.lower():
        return {
            'platform_name': 'WIO Bank',
            'platform_type': 'Digital Investment Platform',
            'app_name': 'WIO Invest App',
            'features': [
                'Commission-free stock trading',
                'Real-time market data and analytics',
                'Fractional share investing',
                'Portfolio tracking and insights',
                'UAE and US market access',
                'Sharia-compliant investment options'
            ],
            'setup_steps': [
                'Download WIO Invest App from App Store/Google Play',
                'Complete KYC verification with Emirates ID',
                'Fund your account via bank transfer',
                'Browse and select recommended stocks',
                'Set up automated investing if desired'
            ],
            'benefits': [
                'Zero commission on stock trades',
                'Regulated by UAE Central Bank',
                'Seamless integration with WIO banking',
                'Professional research and insights',
                'Mobile-first investment experience'
            ]
        }

    # WIO Personal Saving Spaces for Fixed Income
    elif category.lower() in ['fixed income', 'savings'] or any(term in category.lower() for term in ['bond', 'fixed', 'saving']):
        return {
            'platform_name': 'WIO Bank',
            'platform_type': 'Digital Savings Platform',
            'app_name': 'WIO Personal Saving Spaces',
            'features': [
                'Goal-based savings spaces',
                'Competitive interest rates',
                'Automated savings plans',
                'Round-up savings feature',
                'Instant access to funds',
                'FDIC-equivalent protection'
            ],
            'setup_steps': [
                'Open WIO Bank account if not existing',
                'Access Saving Spaces in WIO app',
                'Create goal-specific savings space',
                'Set up automatic transfers',
                'Monitor progress with visual tracking'
            ],
            'benefits': [
                'Higher returns than traditional savings',
                'Flexible access to your money',
                'Goal-oriented saving approach',
                'No minimum balance requirements',
                'Integrated with WIO ecosystem'
            ]
        }

    # Default WIO recommendation for other categories
    else:
        return {
            'platform_name': 'WIO Bank',
            'platform_type': 'Comprehensive Digital Banking',
            'app_name': 'WIO Personal App',
            'features': [
                'All-in-one financial platform',
                'Investment and savings integration',
                'Advanced financial planning tools',
                'Multi-currency support',
                'Real-time spending insights'
            ],
            'setup_steps': [
                'Download WIO app and create account',
                'Complete identity verification',
                'Explore investment and savings options',
                'Set up your financial goals',
                'Begin your investment journey'
            ],
            'benefits': [
                'Unified financial management',
                'Cutting-edge technology platform',
                'Personalized financial insights',
                'Competitive rates and fees',
                'Award-winning customer service'
            ]
        }
    retriver = None

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize Ollama model
try:
    model = OllamaLLM(model="llama3.2")
    OLLAMA_AVAILABLE = True
    print("Ollama model initialized successfully")
except Exception as e:
    print(f"Warning: Could not initialize Ollama model: {e}")
    OLLAMA_AVAILABLE = False
    model = None

# Enhanced dynamic template for structured financial planning with historical data context
template = """
You are an advanced AI financial planner with access to real-time market data, historical performance analysis, and comprehensive investment research.

HISTORICAL MARKET CONTEXT & AVAILABLE INSTRUMENTS:
{instruments}

USER PROFILE:
- Age: {age} years
- Retirement Age: {retirement_age} years
- Annual Income: ${annual_income:,.0f}
- Annual Expenses: ${annual_expenses:,.0f}
- Current Savings: ${current_savings:,.0f}
- Risk Tolerance: {risk_tolerance}
- Investment Goals: {goals}
- Sharia Compliant: {is_sharia_compliant}
- Preferred Market: {preferred_market}

FINANCIAL ANALYSIS:
- Investment Horizon: {investment_horizon} years
- Monthly Savings Capacity: ${monthly_savings_capacity:,.0f}
- Annual Savings Rate: {savings_rate:.1%}

INSTRUCTIONS:
Based on the user's profile and historical market data provided above, create a DYNAMIC and PERSONALIZED financial plan.

DO NOT use generic allocations. Instead:
1. Analyze the user's specific risk tolerance, age, and investment horizon
2. Consider historical performance data of available instruments
3. Calculate optimal allocation percentages based on Modern Portfolio Theory
4. Recommend specific instruments with actual symbols and names from the context
5. Provide realistic expected returns based on historical data
6. Consider market conditions and economic factors

REQUIRED RESPONSE STRUCTURE:

1. EXECUTIVE SUMMARY
Brief analysis of the user's financial position and recommended strategy approach.

2. PORTFOLIO RECOMMENDATIONS
List 3-5 SPECIFIC instruments with:
- Exact instrument name and symbol from the context
- Precise allocation percentage (must total 100%)
- Investment amount in dollars
- Rationale based on historical performance and user profile
- Expected annual return based on historical data

3. RISK ASSESSMENT
Provide structured risk analysis with:
- Risk Level: Specific risk level (e.g., "Moderate Risk (5/10)")
- Description: Brief description of the risk approach
- Suitability: Who this risk level is suitable for
- Allocation Focus: What types of investments to focus on
- Time Factor: How the investment timeline affects risk tolerance
- Age Factor: How the client's age impacts risk capacity

4. TIME HORIZON ANALYSIS
Provide structured timeline analysis with:
- Horizon Category: Classify as Short-term/Medium-term/Long-term with years
- Strategy: Investment strategy based on timeline
- Flexibility: Level of flexibility available
- Milestones: Break down into phases:
  * Short-term (Years 1-5): What to focus on
  * Medium-term (Years 6-15): Key objectives
  * Long-term (Years 16+): Final phase goals
- Retirement Readiness: Assessment of retirement preparation

5. MONTHLY SAVINGS NEEDED
Calculate specific monthly investment amounts to achieve:
- Retirement income replacement of 80% current income
- Emergency fund targets
- Goal-specific savings rates

6. GOAL ACHIEVEMENT TIMELINE
Realistic timeline for achieving:
- Retirement readiness
- Each specific goal mentioned
- Milestone checkpoints

7. GOAL RISKS AND MITIGATION
For each major goal (retirement, wealth building, etc.), provide:
- Goal Name: [Goal Name]
- Potential Risks: List 3-4 specific risks as bullet points
- Mitigation Strategies: List 3-4 specific strategies as bullet points

8. ADDITIONAL ADVICE
Provide 4-6 specific, actionable pieces of financial advice as bullet points:
- Tax optimization strategies
- Emergency fund recommendations
- Regular review schedule
- Investment best practices
- Market-specific advice
- Compliance considerations

9. COMPLIANCE NOTES
If Sharia compliance required, specify which recommended instruments are compliant.

CRITICAL: Base ALL recommendations on the actual historical data and instruments provided in the context. Use real performance metrics, not generic assumptions.
"""

prompt = ChatPromptTemplate.from_template(template)

def clean_nan_values(value):
    """Convert NaN values and numpy types to JSON-serializable values"""
    import math
    import numpy as np

    if value is None:
        return None
    elif isinstance(value, (np.integer, np.int64, np.int32)):
        return int(value)
    elif isinstance(value, (np.floating, np.float64, np.float32)):
        if math.isnan(value):
            return None
        return float(value)
    elif isinstance(value, float) and math.isnan(value):
        return None
    return value

def calculate_projected_wealth(monthly_investment, annual_return, years):
    """Calculate projected wealth using compound interest formula"""
    if annual_return <= 0 or years <= 0 or monthly_investment <= 0:
        return monthly_investment * 12 * years

    monthly_rate = annual_return / 12
    total_months = years * 12

    # Future value of annuity formula: PMT * [((1 + r)^n - 1) / r]
    if monthly_rate > 0:
        future_value = monthly_investment * (((1 + monthly_rate) ** total_months - 1) / monthly_rate)
    else:
        future_value = monthly_investment * total_months

    return future_value

def structure_risk_assessment(raw_text, user_data, financial_metrics):
    """Structure risk assessment into user-friendly format"""
    if not raw_text or len(raw_text.strip()) < 10:
        # Generate structured risk assessment based on user profile
        risk_tolerance = user_data.get('risk_tolerance', 'moderate').lower()
        age = user_data.get('age', 35)
        investment_horizon = financial_metrics.get('investment_horizon', 30)

        # Dynamic risk level calculation based on user profile
        risk_score = 5  # Default moderate
        if risk_tolerance == 'conservative':
            risk_score = 3
        elif risk_tolerance == 'aggressive':
            risk_score = 7

        # Adjust based on age and timeline
        if age < 35 and investment_horizon > 20:
            risk_score = min(risk_score + 1, 9)
        elif age > 50 or investment_horizon < 10:
            risk_score = max(risk_score - 1, 2)

        risk_level_text = f"{risk_tolerance.title()} Risk ({risk_score}/10)"

        # Dynamic descriptions based on actual profile
        descriptions = {
            'conservative': 'Capital preservation focused with minimal volatility',
            'moderate': 'Balanced approach between growth and stability',
            'aggressive': 'Growth-focused with higher volatility tolerance'
        }

        suitability_map = {
            'conservative': 'Investors prioritizing stability over growth',
            'moderate': 'Long-term investors comfortable with market fluctuations',
            'aggressive': 'Young investors with long investment horizons'
        }

        allocation_map = {
            'conservative': 'Bonds, fixed deposits, and stable value funds',
            'moderate': 'Mix of stocks, bonds, and alternative investments',
            'aggressive': 'Growth stocks, emerging markets, and high-yield investments'
        }

        return {
            'risk_level': risk_level_text,
            'description': descriptions.get(risk_tolerance, descriptions['moderate']),
            'suitability': suitability_map.get(risk_tolerance, suitability_map['moderate']),
            'recommended_allocation': allocation_map.get(risk_tolerance, allocation_map['moderate']),
            'time_factor': f"With {investment_horizon} years to invest, {'higher' if investment_horizon > 15 else 'moderate'} risk tolerance is appropriate",
            'age_factor': f"At age {age}, you have {'ample' if age < 40 else 'sufficient' if age < 50 else 'limited'} time to recover from market downturns"
        }
    else:
        # Parse LLM response for structured data
        lines = raw_text.strip().split('\n')
        structured_data = {
            'description': raw_text.strip()
        }

        # Extract specific fields from LLM response
        for line in lines:
            line = line.strip()
            if line.lower().startswith('risk level:'):
                structured_data['risk_level'] = line.split(':', 1)[1].strip()
            elif line.lower().startswith('description:'):
                structured_data['description'] = line.split(':', 1)[1].strip()
            elif line.lower().startswith('suitability:') or line.lower().startswith('suitable for:'):
                structured_data['suitability'] = line.split(':', 1)[1].strip()
            elif line.lower().startswith('allocation focus:') or line.lower().startswith('focus:'):
                structured_data['recommended_allocation'] = line.split(':', 1)[1].strip()
            elif line.lower().startswith('time factor:'):
                structured_data['time_factor'] = line.split(':', 1)[1].strip()
            elif line.lower().startswith('age factor:'):
                structured_data['age_factor'] = line.split(':', 1)[1].strip()

        # Ensure we have at least basic fields
        if 'risk_level' not in structured_data:
            structured_data['risk_level'] = f"{user_data.get('risk_tolerance', 'moderate').title()} Risk Profile"
        if 'suitability' not in structured_data:
            structured_data['suitability'] = f"Suitable for {user_data.get('risk_tolerance', 'moderate')} risk investors"

        return structured_data

def structure_time_horizon_analysis(raw_text, user_data, financial_metrics):
    """Structure time horizon analysis into user-friendly format"""
    if not raw_text or len(raw_text.strip()) < 10:
        # Generate structured time horizon analysis
        investment_horizon = financial_metrics.get('investment_horizon', 30)
        age = user_data.get('age', 35)
        retirement_age = user_data.get('retirement_age', 65)

        if investment_horizon >= 25:
            horizon_category = 'Long-term'
            strategy = 'Growth-focused strategy with equity emphasis'
            flexibility = 'High flexibility to weather market cycles'
        elif investment_horizon >= 15:
            horizon_category = 'Medium-term'
            strategy = 'Balanced growth and income strategy'
            flexibility = 'Moderate flexibility with some risk management'
        else:
            horizon_category = 'Short-term'
            strategy = 'Conservative income-focused strategy'
            flexibility = 'Limited flexibility, capital preservation priority'

        return {
            'horizon_category': f"{horizon_category} ({investment_horizon} years)",
            'strategy': strategy,
            'flexibility': flexibility,
            'milestones': {
                'short_term': f"Years 1-5: Build emergency fund and establish investment routine",
                'medium_term': f"Years 6-15: Accumulate wealth and optimize portfolio allocation",
                'long_term': f"Years 16-{investment_horizon}: Maximize growth and prepare for retirement"
            },
            'retirement_readiness': f"Target retirement at age {retirement_age} with {investment_horizon} years of wealth accumulation"
        }
    else:
        # Parse existing LLM response into structured format
        return {
            'description': raw_text.strip(),
            'horizon_category': f"{financial_metrics.get('investment_horizon', 30)}-year investment horizon",
            'strategy': "Customized strategy based on your timeline and goals"
        }

def parse_goal_risks_mitigation(raw_text, user_data):
    """Parse goal risks and mitigation strategies from LLM response"""
    if not raw_text or len(raw_text.strip()) < 10:
        # Generate default goal risks based on user profile
        goals = user_data.get('goals', ['retirement'])
        if isinstance(goals, str):
            goals = [goals]

        default_risks = {
            'retirement': {
                'risks': [
                    'Market volatility affecting long-term returns',
                    'Inflation eroding purchasing power over time',
                    'Sequence of returns risk near retirement',
                    'Healthcare cost increases in retirement'
                ],
                'mitigation': [
                    'Diversified portfolio across asset classes',
                    'Inflation-protected securities allocation',
                    'Gradual shift to conservative investments near retirement',
                    'Health savings account and insurance planning'
                ]
            },
            'wealth_building': {
                'risks': [
                    'Market cycles affecting growth trajectory',
                    'Lifestyle inflation reducing savings rate',
                    'Economic downturns impacting income',
                    'Lack of investment discipline'
                ],
                'mitigation': [
                    'Dollar-cost averaging strategy',
                    'Automatic savings and investment plans',
                    'Emergency fund maintenance',
                    'Regular portfolio reviews and rebalancing'
                ]
            },
            'education': {
                'risks': [
                    'Education cost inflation exceeding general inflation',
                    'Fixed timeline constraints',
                    'Currency fluctuations for overseas education',
                    'Changing education landscape and costs'
                ],
                'mitigation': [
                    'Education-specific savings plans',
                    'Conservative approach as deadline approaches',
                    'Scholarship and grant research',
                    'Alternative education funding options'
                ]
            }
        }

        result = {}
        for goal in goals:
            goal_key = goal.lower()
            if goal_key in default_risks:
                result[goal] = default_risks[goal_key]
            else:
                result[goal] = {
                    'risks': [
                        'Market uncertainty affecting goal timeline',
                        'Inflation impact on goal costs',
                        'Income volatility affecting savings',
                        'Changing personal circumstances'
                    ],
                    'mitigation': [
                        'Flexible investment strategy',
                        'Regular goal review and adjustment',
                        'Diversified savings approach',
                        'Contingency planning'
                    ]
                }

        return result
    else:
        # Parse LLM response for goal risks and mitigation
        goals_data = {}

        # Split by goal sections
        goal_sections = raw_text.split('Goal Name:')

        for section in goal_sections[1:]:  # Skip first empty section
            lines = section.strip().split('\n')
            if not lines:
                continue

            goal_name = lines[0].strip()
            risks = []
            mitigation = []

            current_section = None
            for line in lines[1:]:
                line = line.strip()
                if 'potential risks' in line.lower():
                    current_section = 'risks'
                elif 'mitigation' in line.lower():
                    current_section = 'mitigation'
                elif line.startswith('-') or line.startswith('•'):
                    item = line.lstrip('-•').strip()
                    if current_section == 'risks':
                        risks.append(item)
                    elif current_section == 'mitigation':
                        mitigation.append(item)

            if goal_name and (risks or mitigation):
                goals_data[goal_name] = {
                    'risks': risks if risks else ['Market uncertainty', 'Timeline constraints'],
                    'mitigation': mitigation if mitigation else ['Regular monitoring', 'Flexible strategy']
                }

        return goals_data if goals_data else parse_goal_risks_mitigation("", user_data)

def parse_additional_advice(raw_text, user_data):
    """Parse additional advice from LLM response into bullet points"""
    if not raw_text or len(raw_text.strip()) < 10:
        # Generate default advice based on user profile
        risk_tolerance = user_data.get('risk_tolerance', 'moderate').lower()
        age = user_data.get('age', 35)
        sharia_compliant = user_data.get('sharia_compliant', False)

        default_advice = [
            "Review and rebalance your portfolio quarterly to maintain target allocation",
            "Increase monthly investments by 5-10% annually as income grows",
            "Maintain an emergency fund covering 3-6 months of expenses",
            "Consider tax-advantaged accounts for retirement savings",
            "Monitor market conditions and adjust strategy during major economic shifts"
        ]

        if sharia_compliant:
            default_advice.append("Ensure all investments maintain Sharia compliance through regular screening")

        if age < 40:
            default_advice.append("Take advantage of long investment horizon with growth-focused allocations")
        elif age > 50:
            default_advice.append("Begin gradual shift towards more conservative investments")

        if risk_tolerance == 'conservative':
            default_advice.append("Focus on capital preservation with stable, income-generating investments")
        elif risk_tolerance == 'aggressive':
            default_advice.append("Maximize growth potential while maintaining appropriate diversification")

        return default_advice
    else:
        # Parse LLM response for bullet points
        advice_list = []
        lines = raw_text.strip().split('\n')

        for line in lines:
            line = line.strip()
            if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                advice = line.lstrip('-•*').strip()
                if advice and len(advice) > 10:  # Filter out very short items
                    advice_list.append(advice)

        # If no bullet points found, try to split by sentences
        if not advice_list:
            sentences = raw_text.replace('\n', ' ').split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence and len(sentence) > 20:
                    advice_list.append(sentence)

        return advice_list if advice_list else parse_additional_advice("", user_data)
# TODO("DO not use investment DB instead use ollama3.2 / vector DB/ Gemini2.5 pro generated recommendations")
def get_specific_instrument_recommendations(user_data):
    """Get specific instrument recommendations from the database"""
    if not DATABASE_AVAILABLE:
        return []

    try:
        db = InvestmentDatabase()

        # Determine risk level
        risk_map = {'conservative': 3, 'moderate': 6, 'aggressive': 9}
        risk_level = risk_map.get(user_data['risk_tolerance'], 6)

        # Get instruments based on user preferences
        if user_data.get('is_sharia_compliant', False):
            instruments_df = db.get_sharia_compliant_instruments()
        else:
            instruments_df = db.get_all_instruments()

        # Filter by market preference
        if user_data.get('preferred_market') and user_data['preferred_market'] != 'BOTH':
            instruments_df = instruments_df[instruments_df['market'] == user_data['preferred_market']]

        # Filter by risk level (within range)
        risk_range = 2
        instruments_df = instruments_df[
            (instruments_df['risk_level'] >= max(1, risk_level - risk_range)) &
            (instruments_df['risk_level'] <= min(10, risk_level + risk_range))
        ]

        # Get performance metrics for all instruments
        performance_df = db.get_performance_metrics()

        # Merge instruments with performance data
        merged_df = instruments_df.merge(performance_df, on='symbol', how='left')

        # Select top instruments by category
        recommendations = []

        # Equity recommendations
        equity_instruments = merged_df[merged_df['category'].str.contains('Stock|ETF|Equity', case=False, na=False)]
        if not equity_instruments.empty:
            # Sort by Sharpe ratio and one-year return
            equity_instruments = equity_instruments.sort_values(['sharpe_ratio', 'one_year_return'], ascending=False, na_position='last')
            top_equity = equity_instruments.head(3)

            for _, instrument in top_equity.iterrows():
                recommendations.append({
                    'symbol': instrument['symbol'],
                    'name': instrument['name'],
                    'category': 'Equity',
                    'allocation_percentage': 0,  # Will be set later
                    'investment_amount': 0,  # Will be set later
                    'rationale': f"{instrument['description']}. Expected return: {clean_nan_values(instrument.get('one_year_return', 0.08)) or 0.08*100:.1f}%",
                    'risk_level': instrument['risk_level'],
                    'expected_return': clean_nan_values(instrument.get('one_year_return', 0.08)) or 0.08,
                    'market': instrument['market'],
                    'currency': instrument['currency'],
                    'min_investment': clean_nan_values(instrument['min_investment']),
                    'expense_ratio': clean_nan_values(instrument.get('expense_ratio')),
                    'dividend_yield': clean_nan_values(instrument.get('dividend_yield')),
                    'volatility': clean_nan_values(instrument.get('volatility')),
                    'sharpe_ratio': clean_nan_values(instrument.get('sharpe_ratio')),
                    'ytd_return': clean_nan_values(instrument.get('ytd_return')),
                    'three_year_return': clean_nan_values(instrument.get('three_year_return')),
                    'five_year_return': clean_nan_values(instrument.get('five_year_return')),
                    'max_drawdown': clean_nan_values(instrument.get('max_drawdown')),
                    'platform_recommendation': get_wio_platform_recommendation('Equity', instrument['market'])
                })

        # Bond recommendations
        bond_instruments = merged_df[merged_df['category'].str.contains('Bond|Sukuk', case=False, na=False)]
        if not bond_instruments.empty:
            bond_instruments = bond_instruments.sort_values(['dividend_yield', 'sharpe_ratio'], ascending=False, na_position='last')
            top_bonds = bond_instruments.head(2)

            for _, instrument in top_bonds.iterrows():
                recommendations.append({
                    'symbol': instrument['symbol'],
                    'name': instrument['name'],
                    'category': 'Fixed Income',
                    'allocation_percentage': 0,
                    'investment_amount': 0,
                    'rationale': f"{instrument['description']}. Yield: {clean_nan_values(instrument.get('dividend_yield', 3.5)) or 3.5:.1f}%",
                    'risk_level': instrument['risk_level'],
                    'expected_return': (clean_nan_values(instrument.get('dividend_yield', 3.5)) or 3.5) / 100,
                    'market': instrument['market'],
                    'currency': instrument['currency'],
                    'min_investment': clean_nan_values(instrument['min_investment']),
                    'expense_ratio': clean_nan_values(instrument.get('expense_ratio')),
                    'dividend_yield': clean_nan_values(instrument.get('dividend_yield')),
                    'volatility': clean_nan_values(instrument.get('volatility')),
                    'sharpe_ratio': clean_nan_values(instrument.get('sharpe_ratio')),
                    'ytd_return': clean_nan_values(instrument.get('ytd_return')),
                    'three_year_return': clean_nan_values(instrument.get('three_year_return')),
                    'five_year_return': clean_nan_values(instrument.get('five_year_return')),
                    'max_drawdown': clean_nan_values(instrument.get('max_drawdown')),
                    'platform_recommendation': get_wio_platform_recommendation('Fixed Income', instrument['market'])
                })

        # REIT recommendations
        reit_instruments = merged_df[merged_df['category'].str.contains('REIT|Real Estate', case=False, na=False)]
        if not reit_instruments.empty:
            reit_instruments = reit_instruments.sort_values(['dividend_yield', 'one_year_return'], ascending=False, na_position='last')
            top_reits = reit_instruments.head(1)

            for _, instrument in top_reits.iterrows():
                recommendations.append({
                    'symbol': instrument['symbol'],
                    'name': instrument['name'],
                    'category': 'Real Estate',
                    'allocation_percentage': 0,
                    'investment_amount': 0,
                    'rationale': f"{instrument['description']}. Dividend yield: {clean_nan_values(instrument.get('dividend_yield', 3.5)) or 3.5:.1f}%",
                    'risk_level': instrument['risk_level'],
                    'expected_return': clean_nan_values(instrument.get('one_year_return', 0.07)) or 0.07,
                    'market': instrument['market'],
                    'currency': instrument['currency'],
                    'min_investment': clean_nan_values(instrument['min_investment']),
                    'expense_ratio': clean_nan_values(instrument.get('expense_ratio')),
                    'dividend_yield': clean_nan_values(instrument.get('dividend_yield')),
                    'volatility': clean_nan_values(instrument.get('volatility')),
                    'sharpe_ratio': clean_nan_values(instrument.get('sharpe_ratio')),
                    'ytd_return': clean_nan_values(instrument.get('ytd_return')),
                    'three_year_return': clean_nan_values(instrument.get('three_year_return')),
                    'five_year_return': clean_nan_values(instrument.get('five_year_return')),
                    'max_drawdown': clean_nan_values(instrument.get('max_drawdown')),
                    'platform_recommendation': get_wio_platform_recommendation('Real Estate', instrument['market'])
                })

        db.close()
        return recommendations

    except Exception as e:
        print(f"Error getting instrument recommendations: {e}")
        return []

def calculate_basic_financial_metrics(user_data):
    """Calculate basic financial metrics"""
    annual_savings_capacity = user_data['annual_salary'] - user_data['annual_expenses']
    monthly_savings_capacity = annual_savings_capacity / 12
    savings_rate = annual_savings_capacity / user_data['annual_salary'] if user_data['annual_salary'] > 0 else 0
    investment_horizon = user_data['retirement_age'] - user_data['age']
    
    # Basic retirement calculation (simplified)
    retirement_expenses = user_data['annual_expenses']
    retirement_years = 25  # Assume 25 years in retirement
    retirement_corpus_needed = retirement_expenses * retirement_years
    
    # Future value calculation with 8% return assumption
    monthly_contribution = monthly_savings_capacity
    annual_return = 0.08
    months = investment_horizon * 12
    
    if monthly_contribution > 0:
        # Future value of annuity formula
        future_value_contributions = monthly_contribution * (((1 + annual_return/12)**months - 1) / (annual_return/12))
        # Future value of current savings
        future_value_current = user_data['current_savings'] * ((1 + annual_return)**investment_horizon)
        total_accumulated = future_value_contributions + future_value_current
    else:
        total_accumulated = user_data['current_savings'] * ((1 + annual_return)**investment_horizon)
    
    shortfall = max(0, retirement_corpus_needed - total_accumulated)
    additional_monthly_needed = 0
    
    if shortfall > 0 and investment_horizon > 0:
        # Calculate additional monthly savings needed
        monthly_rate = annual_return / 12
        if monthly_rate > 0:
            denominator = ((1 + monthly_rate)**months - 1) / monthly_rate
            if denominator > 0:
                additional_monthly_needed = shortfall / denominator
            else:
                additional_monthly_needed = shortfall / months  # Fallback for zero interest
        else:
            additional_monthly_needed = shortfall / months  # Fallback for zero interest

        # Ensure no NaN values
        if not isinstance(additional_monthly_needed, (int, float)) or additional_monthly_needed != additional_monthly_needed:
            additional_monthly_needed = 0
    
    return {
        'monthly_savings_capacity': monthly_savings_capacity,
        'savings_rate': savings_rate,
        'investment_horizon': investment_horizon,
        'retirement_corpus_needed': retirement_corpus_needed,
        'total_accumulated': total_accumulated,
        'shortfall': shortfall,
        'additional_monthly_needed': additional_monthly_needed,
        'is_on_track': shortfall <= 0
    }

def generate_dynamic_recommendations(user_data, financial_metrics):
    """Generate dynamic recommendations based on user profile and historical data"""
    print(f"🔍 DEBUG - generate_dynamic_recommendations called")
    print(f"🔍 DEBUG - DATABASE_AVAILABLE: {DATABASE_AVAILABLE}")

    if not DATABASE_AVAILABLE:
        print(f"🔍 DEBUG - Database not available, returning empty list")
        return []

    try:
        db = InvestmentDatabase()
        print(f"🔍 DEBUG - Database connection established")

        # Normalize user data for consistency (handle both sharia_compliant and is_sharia_compliant)
        is_sharia_compliant = user_data.get('is_sharia_compliant', user_data.get('sharia_compliant', False))

        # Get all available instruments
        if is_sharia_compliant:
            instruments_df = db.get_sharia_compliant_instruments()
            print(f"🔍 DEBUG - Getting Sharia compliant instruments")
        else:
            instruments_df = db.get_all_instruments()
            print(f"🔍 DEBUG - Getting all instruments")

        print(f"🔍 DEBUG - Found {(instruments_df)} instruments")

        # Filter by market preference
        if user_data.get('preferred_market') and user_data['preferred_market'] != 'BOTH':
            fl_instruments_df = instruments_df[instruments_df['market'] == user_data['preferred_market']]
            print(f"🔍 DEBUG - Filtered by market {user_data['preferred_market']}: {len(fl_instruments_df)} instruments")

        # Get performance metrics
        performance_df = db.get_performance_metrics()
        print(f"🔍 DEBUG - Found {len(performance_df)} performance records")
        merged_df = instruments_df.merge(performance_df, on='symbol', how='left')
        print(f"🔍 DEBUG - Merged data: {len(merged_df)} records")

        # Dynamic risk-based allocation strategy
        risk_tolerance = user_data.get('risk_tolerance', 'moderate').lower()
        age = user_data.get('age', 35)
        investment_horizon = user_data.get('retirement_age', 65) - age

        # Calculate dynamic allocation based on multiple factors
        if risk_tolerance == 'conservative' or age > 55 or investment_horizon < 10:
            equity_allocation = max(20, 100 - age)  # Age-based rule
            bond_allocation = min(70, age + 10)
            reit_allocation = 10
        elif risk_tolerance == 'aggressive' and age < 40 and investment_horizon > 20:
            equity_allocation = min(80, 120 - age)
            bond_allocation = max(10, age - 20)
            reit_allocation = 20
        else:  # Moderate
            equity_allocation = 100 - age
            bond_allocation = age
            reit_allocation = 15

        # Normalize allocations to 100%
        total = equity_allocation + bond_allocation + reit_allocation
        equity_allocation = (equity_allocation / total) * 100
        bond_allocation = (bond_allocation / total) * 100
        reit_allocation = (reit_allocation / total) * 100

        recommendations = []
        monthly_capacity = financial_metrics.get('monthly_savings_capacity', 3000)

        # Select best performing instruments by category
        # Equity recommendations
        equity_instruments = merged_df[merged_df['category'].str.contains('Stock|ETF|Equity', case=False, na=False)]
        if not equity_instruments.empty:
            # Sort by risk-adjusted returns (Sharpe ratio)
            equity_instruments = equity_instruments.sort_values(['sharpe_ratio', 'one_year_return'], ascending=False, na_position='last')
            top_equity = equity_instruments.head(2)  # Top 2 equity instruments

            allocation_per_equity = equity_allocation / len(top_equity)
            for _, instrument in top_equity.iterrows():
                recommendations.append({
                    'symbol': instrument['symbol'],
                    'name': instrument['name'],
                    'category': 'Equity',
                    'allocation_percentage': round(allocation_per_equity, 1),
                    'investment_amount': round(monthly_capacity * (allocation_per_equity / 100), 2),
                    'rationale': f"Selected for {risk_tolerance} risk profile. {instrument['description']}. Expected return: {clean_nan_values(instrument.get('one_year_return', 0.08)) or 0.08*100:.1f}%",
                    'risk_level': instrument['risk_level'],
                    'expected_return': clean_nan_values(instrument.get('one_year_return', 0.08)) or 0.08,
                    'market': instrument['market'],
                    'platform_recommendation': get_wio_platform_recommendation('Equity', instrument['market'])
                })

        # Bond recommendations
        bond_instruments = merged_df[merged_df['category'].str.contains('Bond|Sukuk', case=False, na=False)]
        if not bond_instruments.empty and bond_allocation > 0:
            bond_instruments = bond_instruments.sort_values(['dividend_yield', 'sharpe_ratio'], ascending=False, na_position='last')
            top_bond = bond_instruments.head(1).iloc[0]

            recommendations.append({
                'symbol': top_bond['symbol'],
                'name': top_bond['name'],
                'category': 'Fixed Income',
                'allocation_percentage': round(bond_allocation, 1),
                'investment_amount': round(monthly_capacity * (bond_allocation / 100), 2),
                'rationale': f"Provides stability for {risk_tolerance} investor. {top_bond['description']}. Yield: {clean_nan_values(top_bond.get('dividend_yield', 3.5)) or 3.5:.1f}%",
                'risk_level': top_bond['risk_level'],
                'expected_return': (clean_nan_values(top_bond.get('dividend_yield', 3.5)) or 3.5) / 100,
                'market': top_bond['market'],
                'platform_recommendation': get_wio_platform_recommendation('Fixed Income', top_bond['market'])
            })

        # REIT recommendations
        reit_instruments = merged_df[merged_df['category'].str.contains('REIT|Real Estate', case=False, na=False)]
        if not reit_instruments.empty and reit_allocation > 0:
            reit_instruments = reit_instruments.sort_values(['dividend_yield', 'one_year_return'], ascending=False, na_position='last')
            top_reit = reit_instruments.head(1).iloc[0]

            recommendations.append({
                'symbol': top_reit['symbol'],
                'name': top_reit['name'],
                'category': 'Real Estate',
                'allocation_percentage': round(reit_allocation, 1),
                'investment_amount': round(monthly_capacity * (reit_allocation / 100), 2),
                'rationale': f"Diversification and inflation hedge. {top_reit['description']}. Dividend yield: {clean_nan_values(top_reit.get('dividend_yield', 3.5)) or 3.5:.1f}%",
                'risk_level': top_reit['risk_level'],
                'expected_return': clean_nan_values(top_reit.get('one_year_return', 0.07)) or 0.07,
                'market': top_reit['market'],
                'platform_recommendation': get_wio_platform_recommendation('Real Estate', top_reit['market'])
            })

        db.close()
        print(f"*** generate_dynamic_recommendations ***: {len(recommendations)} instruments")
        return recommendations

    except Exception as e:
        print(f"Error generating dynamic recommendations: {e}")
        return []

def parse_llm_response_to_structured_data(llm_response, user_data, financial_metrics):
    """Parse LLM response into structured data for React UI"""
    
    # Extract sections using regex patterns
    def extract_section(pattern, text):
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else ""
    
    print(f"parse_llm_response_to_structured_data")

    # Parse different sections with improved regex patterns to handle numbered sections
    executive_summary = extract_section(r'(?:\d+\.\s*)?(?:\*\*)?EXECUTIVE SUMMARY(?:\*\*)?[:\s]*\n(.*?)(?=\n(?:\d+\.\s*)?(?:\*\*)?[A-Z]|\Z)', llm_response)

    # More precise portfolio recommendations extraction - only capture actual investment recommendations
    portfolio_recommendations = extract_section(r'(?:\d+\.\s*)?(?:\*\*)?PORTFOLIO RECOMMENDATIONS(?:\*\*)?[:\s]*\n(.*?)(?=\n(?:\d+\.\s*)?(?:\*\*)?(?:RISK ASSESSMENT|TIME HORIZON|MONTHLY SAVINGS|ADDITIONAL ADVICE|COMPLIANCE)|\Z)', llm_response)

    # If the above doesn't work, try alternative patterns but be more selective
    if not portfolio_recommendations or len(portfolio_recommendations.strip()) < 50:
        print("🔍 DEBUG - First extraction failed, trying alternative patterns...")

        # Try to find the section that starts with PORTFOLIO RECOMMENDATIONS and includes investment items
        portfolio_match = re.search(r'(?:\*\*)?PORTFOLIO RECOMMENDATIONS(?:\*\*)?[:\s]*\n(.*?)(?=\n(?:\*\*)?(?:RISK ASSESSMENT|TIME HORIZON|MONTHLY SAVINGS|ADDITIONAL ADVICE|COMPLIANCE)|\Z)', llm_response, re.DOTALL)
        if portfolio_match:
            portfolio_recommendations = portfolio_match.group(1)
            print(f"🔍 DEBUG - Alternative pattern 1 found: {len(portfolio_recommendations)} chars")
        else:
            # Try to find any section with investment allocations (but not return percentages)
            portfolio_match = re.search(r'((?:[*•-]\s*\*\*.*?(?:ETF|Stock|Bond|Fund|Investment|Inc\.|UCITS|Equity|Growth|Real Estate).*?(?:\d+(?:\.\d+)?)%.*?\n(?:.*?Rationale:.*?\n)?)+)', llm_response, re.DOTALL)
            if portfolio_match:
                portfolio_recommendations = portfolio_match.group(1)
                print(f"🔍 DEBUG - Alternative pattern 2 found: {len(portfolio_recommendations)} chars")
            else:
                # Last resort: find numbered investment list with allocation percentages
                portfolio_match = re.search(r'((?:\d+\.\s*\*\*.*?(?:ETF|Stock|Bond|Fund|Investment|Inc\.|UCITS|Equity|Growth|Real Estate).*?(?:\d+(?:\.\d+)?)%.*?\n(?:.*?\n)*?)+)', llm_response, re.DOTALL)
                if portfolio_match:
                    portfolio_recommendations = portfolio_match.group(1)
                    print(f"🔍 DEBUG - Alternative pattern 3 found: {len(portfolio_recommendations)} chars")

    # Extract and structure risk assessment and time horizon analysis
    risk_assessment_raw = extract_section(r'(?:\d+\.\s*)?(?:\*\*)?RISK ASSESSMENT(?:\*\*)?[:\s]*\n(.*?)(?=\n(?:\d+\.\s*)?(?:\*\*)?[A-Z]|\Z)', llm_response)
    time_horizon_raw = extract_section(r'(?:\d+\.\s*)?(?:\*\*)?TIME HORIZON ANALYSIS(?:\*\*)?[:\s]*\n(.*?)(?=\n(?:\d+\.\s*)?(?:\*\*)?[A-Z]|\Z)', llm_response)

    # Structure risk assessment for better UI display
    risk_assessment = structure_risk_assessment(risk_assessment_raw, user_data, financial_metrics)
    time_horizon = structure_time_horizon_analysis(time_horizon_raw, user_data, financial_metrics)
    monthly_savings = extract_section(r'(?:\d+\.\s*)?(?:\*\*)?MONTHLY SAVINGS NEEDED(?:\*\*)?[:\s]*\n(.*?)(?=\n(?:\d+\.\s*)?(?:\*\*)?[A-Z]|\Z)', llm_response)
    # goal_timeline = extract_section(r'GOAL ACHIEVEMENT TIMELINE[:\s]*\n(.*?)(?=\n\d+\.|\n[A-Z]|\Z)', llm_response)  # Not used - we create structured timeline below
    # Extract dynamic sections
    goal_risks_raw = extract_section(r'(?:\d+\.\s*)?(?:\*\*)?GOAL RISKS AND MITIGATION(?:\*\*)?[:\s]*\n(.*?)(?=\n(?:\d+\.\s*)?(?:\*\*)?[A-Z]|\Z)', llm_response)
    additional_advice_raw = extract_section(r'(?:\d+\.\s*)?(?:\*\*)?ADDITIONAL ADVICE(?:\*\*)?[:\s]*\n(.*?)(?=\n(?:\d+\.\s*)?(?:\*\*)?[A-Z]|\Z)', llm_response)
    compliance_notes = extract_section(r'(?:\d+\.\s*)?(?:\*\*)?COMPLIANCE NOTES(?:\*\*)?[:\s]*\n(.*?)(?=\n(?:\d+\.\s*)?(?:\*\*)?[A-Z]|\Z)', llm_response)

    # Parse dynamic content
    goal_risks_mitigation = parse_goal_risks_mitigation(goal_risks_raw, user_data)
    additional_advice = parse_additional_advice(additional_advice_raw, user_data)
    
    # Parse portfolio recommendations into structured format with improved extraction
    recommendations = []
    print(f"🔍 DEBUG - portfolio_recommendations extracted: '{portfolio_recommendations}'")
    print(f"🔍 DEBUG - portfolio_recommendations length: {len(portfolio_recommendations) if portfolio_recommendations else 0}")

    # Also print first 500 chars of LLM response to debug
    print(f"🔍 DEBUG - LLM response preview: {llm_response[:500]}...")

    if portfolio_recommendations:
        # Use more precise parsing patterns to extract only actual investment recommendations
        lines = portfolio_recommendations.split('\n')

        # Parse multi-line instrument blocks with stricter filtering
        current_instrument = None
        i = 0

        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            # Pattern 1: "* **Investment Name:** XX%" (most common format)
            pattern1 = re.search(r'[*•-]\s*\*\*(.+?):\*\*\s*(\d+(?:\.\d+)?)%', line)
            if pattern1:
                name_part = pattern1.group(1).strip()
                percentage = float(pattern1.group(2))

                # Only process if it looks like an actual investment (contains investment keywords)
                if any(investment_word in name_part.lower() for investment_word in [
                    'etf', 'fund', 'stock', 'bond', 'equity', 'reit', 'investment', 'trust', 'inc', 'corp',
                    'bank', 'properties', 'oil', 'tech', 'growth', 'treasury', 'sukuk', 'gold', 'silver',
                    'tesla', 'apple', 'microsoft', 'amazon', 'google', 'emirates', 'adnoc', 'aldar', 'fab'
                ]) and not any(skip_word in name_part.lower() for skip_word in [
                    'expected annual return', 'annual return', 'return', 'expected return',
                    'risk level', 'sharpe ratio', 'volatility', 'expense ratio',
                    'dividend yield', 'beta', 'standard deviation', 'correlation'
                ]):
                    # Look ahead for additional details
                    additional_details = []
                    j = i + 1
                    while j < len(lines) and lines[j].strip() and not re.search(r'[*•-]\s*\*\*.*?:\*\*\s*\d+(?:\.\d+)?%', lines[j]):
                        additional_details.append(lines[j].strip())
                        j += 1

                    full_details = line
                    if additional_details:
                        full_details += " " + " ".join(additional_details)

                    current_instrument = {
                        'name_part': name_part,
                        'percentage': percentage,
                        'details_part': full_details,
                        'line': line
                    }

                i = j if 'j' in locals() else i + 1
            else:
                # Pattern 2: "1. **Investment Name (XX%):**" or similar numbered format
                pattern2 = re.search(r'(\d+)\.\s*\*\*(.+?)\s*\((\d+(?:\.\d+)?)%\)', line)
                if pattern2:
                    name_part = pattern2.group(2).strip()
                    percentage = float(pattern2.group(3))

                    # Only process if it looks like an actual investment
                    if any(investment_word in name_part.lower() for investment_word in [
                        'etf', 'fund', 'stock', 'bond', 'equity', 'reit', 'investment', 'trust', 'inc', 'corp',
                        'bank', 'properties', 'oil', 'tech', 'growth', 'treasury', 'sukuk', 'gold', 'silver',
                        'tesla', 'apple', 'microsoft', 'amazon', 'google', 'emirates', 'adnoc', 'aldar', 'fab'
                    ]):
                        # Look ahead for additional details
                        additional_details = []
                        j = i + 1
                        while j < len(lines) and lines[j].strip() and not re.search(r'\d+\.\s*\*\*.*?\*\*', lines[j]):
                            additional_details.append(lines[j].strip())
                            j += 1

                        full_details = line
                        if additional_details:
                            full_details += " " + " ".join(additional_details)

                        current_instrument = {
                            'name_part': name_part,
                            'percentage': percentage,
                            'details_part': full_details,
                            'line': line
                        }

                    i = j if 'j' in locals() else i + 1
                else:
                    i += 1
                    continue

            # Process the current instrument
            if current_instrument:
                name_part = current_instrument['name_part']
                percentage = current_instrument['percentage']
                details_part = current_instrument['details_part']
                investment_amount = (financial_metrics['monthly_savings_capacity'] * percentage / 100)

                # Extract symbol if present in parentheses
                symbol_match = re.search(r'\(([A-Z0-9]+)\)', name_part)
                if not symbol_match:
                    # Try to extract from details
                    symbol_match = re.search(r'\(([A-Z0-9]+)\)', details_part)
                symbol = symbol_match.group(1) if symbol_match else name_part[:10].upper().replace(' ', '')

                # Clean name by removing symbol in parentheses
                clean_name = re.sub(r'\s*\([^)]+\)', '', name_part).strip()

                # Determine category based on name and context
                category = 'Investment'
                name_lower = clean_name.lower()
                details_lower = details_part.lower()

                if any(keyword in name_lower + details_lower for keyword in ['stock', 'equity', 'etf', 'share', 'growth', 'tech', 'large-cap', 'nasdaq']):
                    category = 'Equity'
                elif any(keyword in name_lower + details_lower for keyword in ['bond', 'fixed', 'saving', 'treasury', 'sukuk']):
                    category = 'Fixed Income'
                elif any(keyword in name_lower + details_lower for keyword in ['reit', 'real estate', 'property']):
                    category = 'Real Estate'
                elif any(keyword in name_lower + details_lower for keyword in ['commodity', 'gold', 'oil']):
                    category = 'Commodities'

                # Extract expected return if mentioned
                return_match = re.search(r'(\d+(?:\.\d+)?)%.*return', details_part.lower())
                expected_return = float(return_match.group(1)) / 100 if return_match else 0.08

                # Extract risk level if mentioned
                risk_match = re.search(r'risk.*?(\d+)', details_part.lower())
                risk_level = int(risk_match.group(1)) if risk_match else 5

                # Extract rationale (everything after "Rationale:")
                rationale_match = re.search(r'rationale[:\s]*(.+?)(?:\.|$)', details_part, re.IGNORECASE)
                rationale = rationale_match.group(1).strip() if rationale_match else f"Recommended for {user_data.get('risk_tolerance', 'moderate')} risk profile"

                # Calculate projected wealth for this instrument
                years_to_retirement = user_data.get('retirement_age', 65) - user_data.get('age', 35)
                monthly_investment = investment_amount
                projected_value = calculate_projected_wealth(monthly_investment, expected_return, years_to_retirement)

                print(f"Parsed: {clean_name} ({symbol}) - {percentage}% - Category: {category}")

                if percentage > 0:  # Only add if we found a valid percentage
                    recommendations.append({
                        'symbol': symbol,
                        'name': clean_name,
                        'category': category,
                        'allocation_percentage': float(percentage),
                        'investment_amount': float(investment_amount),
                        'rationale': rationale,
                        'risk_level': int(risk_level),
                        'expected_return': float(expected_return),
                        'projected_wealth': float(projected_value),
                        'market': user_data.get('preferred_market', 'UAE'),
                        'platform_recommendation': get_wio_platform_recommendation(category, user_data.get('preferred_market', 'UAE'))
                    })

                current_instrument = None  # Reset for next instrument
    
    # Use LLM-generated recommendations instead of static database ones
    # The recommendations should come from the LLM response, not predefined database entries
    print(f"Using LLM-generated recommendations: {len(recommendations)} instruments")

    # If no LLM recommendations were parsed, create dynamic fallback based on user profile
    if not recommendations:
        # Generate dynamic recommendations using available instruments from database
        recommendations = generate_dynamic_recommendations(user_data, financial_metrics)
        
    print(f"Using generate_dynamic_recommendations: {len(recommendations)} instruments")

    
    # Calculate total allocation
    total_allocation = {}
    for rec in recommendations:
        category = rec['category']
        if category in total_allocation:
            total_allocation[category] += rec['allocation_percentage']
        else:
            total_allocation[category] = rec['allocation_percentage']
    
    # additional_advice is already processed by parse_additional_advice() function
    # and is ready to use as a list - no further processing needed

    # Calculate total projected wealth
    total_monthly_investment = sum(rec['investment_amount'] for rec in recommendations)
    weighted_avg_return = sum(rec['expected_return'] * rec['allocation_percentage']/100 for rec in recommendations) if recommendations else 0.08
    investment_horizon = financial_metrics['investment_horizon']
    total_projected_wealth = calculate_projected_wealth(total_monthly_investment, weighted_avg_return, investment_horizon)

    # Create structured goal achievement timeline (React UI expects Record<string, number>)
    goal_achievement_timeline = {}
    user_goals = user_data.get('goals', ['retirement'])

    # Ensure user_goals is always a list
    if isinstance(user_goals, str):
        user_goals = [user_goals]
    elif not isinstance(user_goals, list):
        user_goals = ['retirement']

    investment_horizon = financial_metrics['investment_horizon']

    for goal in user_goals:
        if goal.lower() == 'retirement':
            years_to_goal = investment_horizon
            goal_achievement_timeline[goal] = years_to_goal
        elif goal.lower() in ['house_purchase', 'house', 'education']:
            # Shorter term goals
            years_to_goal = min(10, investment_horizon)
            goal_achievement_timeline[goal] = years_to_goal
        elif goal.lower() in ['wealth_building', 'emergency_fund', 'emergency']:
            # Medium term goals
            years_to_goal = min(15, investment_horizon)
            goal_achievement_timeline[goal] = years_to_goal
        elif goal.lower() == 'travel':
            # Short term goal
            years_to_goal = min(5, investment_horizon)
            goal_achievement_timeline[goal] = years_to_goal
        else:
            # Default timeline
            years_to_goal = min(12, investment_horizon)
            goal_achievement_timeline[goal] = years_to_goal

    # If no goals specified, add retirement as default
    if not goal_achievement_timeline:
        years_to_goal = investment_horizon
        goal_achievement_timeline['retirement'] = years_to_goal

    return {
        'user_profile': {
            'age': user_data['age'],
            'retirement_age': user_data['retirement_age'],
            'annual_income': user_data['annual_salary'],
            'annual_expenses': user_data['annual_expenses'],
            'current_savings': user_data['current_savings'],
            'monthly_investment': financial_metrics['monthly_savings_capacity'],
            'risk_tolerance': user_data['risk_tolerance'],
            'investment_horizon': financial_metrics['investment_horizon'],
            'goals': user_data['goals'],
            'is_sharia_compliant': user_data['is_sharia_compliant'],
            'preferred_market': user_data['preferred_market'],
            'currency': user_data.get('currency', 'AED')
        },
        'recommendations': recommendations,
        'total_allocation': total_allocation,
        'risk_assessment': risk_assessment or f"Your {user_data['risk_tolerance']} risk profile is suitable for your {financial_metrics['investment_horizon']}-year investment horizon",
        'time_horizon_analysis': time_horizon or f"With {financial_metrics['investment_horizon']} years until retirement, you have time for growth-oriented investments",
        'expected_portfolio_return': weighted_avg_return,
        'total_projected_wealth': total_projected_wealth,
        'monthly_savings_needed': financial_metrics['additional_monthly_needed'],
        'goal_achievement_timeline': goal_achievement_timeline,
        'additional_advice': additional_advice,
        'goal_risks_mitigation': goal_risks_mitigation,
        'compliance_notes': compliance_notes or ("Sharia-compliant investments recommended" if user_data['is_sharia_compliant'] else ""),
        'executive_summary': executive_summary or f"Based on your profile, with ${total_monthly_investment:,.0f} monthly investment, you are projected to accumulate approximately ${total_projected_wealth:,.0f} by age {user_data['retirement_age']}.",
        'financial_metrics': financial_metrics,
        'raw_llm_response': llm_response if OLLAMA_AVAILABLE else "LLM not available - using rule-based recommendations"
    }

@app.route('/api/generate-financial-plan', methods=['POST'])
def generate_financial_plan():
    """Generate financial plan using Ollama LLM or fallback logic"""
    try:
        user_data = request.json
        
        # Validate required fields
        required_fields = ['age', 'retirement_age', 'annual_salary', 'annual_expenses', 'current_savings']
        for field in required_fields:
            if field not in user_data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        print(f"Received user data: {user_data}")

        # Normalize user data fields for consistency
        if 'sharia_compliant' in user_data and 'is_sharia_compliant' not in user_data:
            user_data['is_sharia_compliant'] = user_data['sharia_compliant']
        elif 'is_sharia_compliant' not in user_data:
            user_data['is_sharia_compliant'] = False

        if 'market_type' in user_data and 'preferred_market' not in user_data:
            user_data['preferred_market'] = user_data['market_type']
        elif 'preferred_market' not in user_data:
            user_data['preferred_market'] = 'UAE'

        # Calculate basic financial metrics
        financial_metrics = calculate_basic_financial_metrics(user_data)

        # Get relevant instruments from vector database
        instruments_context = "UAE and US market instruments available for diversified portfolio allocation"
        if VECTORS_AVAILABLE and retriver:
            try:
                # Create a comprehensive query based on user profile
                goals_text = ', '.join(user_data.get('goals', ['retirement planning']))
                risk_text = user_data.get('risk_tolerance', 'moderate')
                market_text = user_data.get('preferred_market', 'UAE')
                sharia_text = "Sharia-compliant" if user_data.get('is_sharia_compliant', False) else ""

                query = f"Investment recommendations for {goals_text} with {risk_text} risk tolerance in {market_text} market {sharia_text}"
                print(f"Vector DB Query: {query}")

                instruments_results = retriver.invoke(query)
                if instruments_results:
                    instruments_context = "\n".join([doc.page_content for doc in instruments_results[:10]])
                    print(f"Retrieved {len(instruments_results)} relevant instrument data points")
                else:
                    print("No vector results found, using default context")
            except Exception as e:
                print(f"Vector retrieval error: {e}")
                instruments_context = "UAE and US market instruments available for diversified portfolio allocation"
        else:
            print("Vector database not available, using default context")

        llm_response = "LLM not available - using rule-based financial planning"

        print(f"llm_response: {llm_response}")

        # Generate session and user IDs for tracking
        session_id = str(uuid.uuid4())
        user_id = user_data.get('user_id', f"user_{uuid.uuid4().hex[:8]}")

        # Get adaptive response strategy from RL feedback system
        response_strategy = {'strategy_type': 'default', 'confidence': 0.5}
        if RL_FEEDBACK_AVAILABLE:
            try:
                response_strategy = get_adaptive_response_strategy(user_data, user_id)
                print(f"🧠 Adaptive strategy: {response_strategy['strategy_type']} (confidence: {response_strategy['confidence']})")
                if response_strategy['recommended_focus']:
                    print(f"📋 Focus areas: {response_strategy['recommended_focus']}")
            except Exception as e:
                print(f"Error getting adaptive strategy: {e}")

        if OLLAMA_AVAILABLE and model:
            try:
                # Create adaptive prompt based on feedback patterns
                adaptive_template = template
                if RL_FEEDBACK_AVAILABLE and response_strategy['strategy_type'] == 'adaptive':
                    adaptive_template = create_adaptive_prompt(template, response_strategy, user_data)
                    print("🎯 Using adaptive prompt based on user feedback patterns")

                # Create adaptive prompt
                adaptive_prompt = ChatPromptTemplate.from_template(adaptive_template)

                # Generate AI response using Ollama with adaptive context
                chain = adaptive_prompt | model

                # Try with the adaptive prompt first
                try:
                    llm_response = chain.invoke({
                        'instruments': instruments_context,
                        'age': user_data['age'],
                        'retirement_age': user_data['retirement_age'],
                        'annual_income': user_data['annual_salary'],
                        'annual_expenses': user_data['annual_expenses'],
                        'current_savings': user_data['current_savings'],
                        'risk_tolerance': user_data.get('risk_tolerance', 'moderate'),
                        'goals': ', '.join(user_data.get('goals', [])),
                        'is_sharia_compliant': 'Yes' if user_data.get('is_sharia_compliant', False) else 'No',
                        'preferred_market': user_data.get('preferred_market', 'UAE'),
                        'investment_horizon': financial_metrics['investment_horizon'],
                        'monthly_savings_capacity': financial_metrics['monthly_savings_capacity'],
                        'savings_rate': financial_metrics['savings_rate']
                    })

                    # Check if response is too short or unhelpful
                    if len(llm_response.strip()) < 100 or "can't help" in llm_response.lower():
                        print("⚠️ LLM response too short, trying simpler prompt...")
                        raise Exception("Response too short")

                except Exception as e:
                    print(f"⚠️ Adaptive prompt failed: {e}, trying simpler prompt...")
                    # Fallback to simpler prompt
                    simple_prompt = ChatPromptTemplate.from_template("""
                    Create a financial plan for a {age}-year-old with ${annual_income:,.0f} income, ${current_savings:,.0f} savings, {risk_tolerance} risk tolerance, retiring at {retirement_age}.

                    Provide:
                    1. EXECUTIVE SUMMARY
                    2. PORTFOLIO RECOMMENDATIONS (3-4 investments with percentages)
                    3. RISK ASSESSMENT
                    4. MONTHLY SAVINGS NEEDED
                    5. ADDITIONAL ADVICE
                    """)

                    simple_chain = simple_prompt | model
                    llm_response = simple_chain.invoke({
                        'age': user_data['age'],
                        'retirement_age': user_data['retirement_age'],
                        'annual_income': user_data['annual_salary'],
                        'current_savings': user_data['current_savings'],
                        'risk_tolerance': user_data.get('risk_tolerance', 'moderate')
                    })
                
                print(f"LLM Response: {llm_response}")

                # Evaluate and improve response using Gemini 2.5 Pro
                if EVALUATOR_AVAILABLE:
                    try:
                        print("Evaluating response with Gemini 2.5 Pro...")
                        evaluation_results, improved_response = evaluate_and_improve_response(
                            llm_response, user_data, financial_metrics
                        )

                        # Use improved response if evaluation was successful
                        if improved_response != llm_response:
                            print("Using improved response from evaluator agent")
                            llm_response = improved_response

                        # Add comprehensive evaluation metadata to response
                        evaluation_metadata = {
                            'evaluator_used': True,
                            'original_score': evaluation_results.get('overall_score', 0),
                            'improvement_applied': evaluation_results.get('improvement_applied', False),
                            'evaluation_timestamp': evaluation_results.get('timestamp', ''),
                            'improvement_details': evaluation_results.get('improvement_details', {}),
                            'detailed_comparison': evaluation_results.get('detailed_comparison', {}),
                            'evaluation_criteria': evaluation_results.get('evaluation_details', {}),
                            'original_evaluation': evaluation_results.get('original_evaluation', {}),
                            'gemini_responses': {
                                'original_response': evaluation_results.get('original_response', ''),
                                'final_response': evaluation_results.get('final_response', improved_response)
                            }
                        }

                    except Exception as e:
                        print(f"Error in evaluator agent: {e}")
                        evaluation_metadata = {
                            'evaluator_used': False,
                            'error': str(e)
                        }
                else:
                    evaluation_metadata = {
                        'evaluator_used': False,
                        'reason': 'Evaluator agent not available'
                    }

            except Exception as e:
                print(f"Error calling Ollama: {e}")
                llm_response = f"LLM Error: {str(e)} - using fallback recommendations"
                evaluation_metadata = {
                    'evaluator_used': False,
                    'reason': 'LLM error occurred'
                }
        else:
            evaluation_metadata = {
                'evaluator_used': False,
                'reason': 'Ollama not available'
            }

        # Parse LLM response into structured data
        structured_plan = parse_llm_response_to_structured_data(llm_response, user_data, financial_metrics)

        # Add evaluation metadata to the response
        structured_plan['evaluation_metadata'] = evaluation_metadata

        # Add response strategy metadata for feedback collection
        structured_plan['response_metadata'] = {
            'session_id': session_id,
            'user_id': user_id,
            'response_strategy': response_strategy,
            'adaptive_prompt_used': RL_FEEDBACK_AVAILABLE and response_strategy['strategy_type'] == 'adaptive',
            'feedback_samples_used': response_strategy.get('total_feedback_samples', 0)
        }

        # Clean all values for JSON serialization
        def clean_for_json(obj):
            """Recursively clean object for JSON serialization"""
            import numpy as np

            if isinstance(obj, dict):
                return {k: clean_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_for_json(item) for item in obj]
            elif isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64, np.float32)):
                return float(obj) if not np.isnan(obj) else None
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif obj is None or isinstance(obj, (str, int, float, bool)):
                return obj
            else:
                return str(obj)

        cleaned_plan = clean_for_json(structured_plan)
        return jsonify(cleaned_plan)
        
    except Exception as e:
        print(f"Error generating financial plan: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/instrument-details/<symbol>', methods=['GET'])
def get_instrument_details(symbol):
    """Get detailed information about a specific instrument"""
    if not DATABASE_AVAILABLE:
        return jsonify({'error': 'Investment database not available'}), 503

    try:
        db = InvestmentDatabase()
        details = db.get_instrument_details(symbol)
        db.close()

        if not details:
            return jsonify({'error': f'Instrument {symbol} not found'}), 404

        # Get historical data for the last year
        db = InvestmentDatabase()
        historical_data = db.get_historical_data(symbol)
        db.close()

        # Convert historical data to chart format
        chart_data = []
        if not historical_data.empty:
            historical_data = historical_data.tail(252)  # Last year of data
            chart_data = [
                {
                    'date': row['date'],
                    'price': row['close_price'],
                    'volume': row['volume']
                }
                for _, row in historical_data.iterrows()
            ]

        return jsonify({
            'instrument_details': details,
            'historical_data': chart_data,
            'data_points': len(chart_data)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/instruments/category/<category>', methods=['GET'])
def get_instruments_by_category(category):
    """Get all instruments in a specific category"""
    if not DATABASE_AVAILABLE:
        return jsonify({'error': 'Investment database not available'}), 503

    try:
        db = InvestmentDatabase()
        instruments = db.get_instruments_by_category(category)
        performance = db.get_performance_metrics()
        db.close()

        # Merge with performance data
        merged = instruments.merge(performance, on='symbol', how='left')

        return jsonify({
            'instruments': merged.to_dict('records'),
            'total_count': len(merged)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit user feedback for reinforcement learning"""
    try:
        feedback_data = request.json

        # Validate required fields
        required_fields = ['rating', 'query', 'response', 'user_profile']
        for field in required_fields:
            if field not in feedback_data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Generate feedback ID if not provided
        if 'feedback_id' not in feedback_data:
            feedback_data['feedback_id'] = str(uuid.uuid4())

        # Generate user ID if not provided
        if 'user_id' not in feedback_data:
            feedback_data['user_id'] = f"user_{uuid.uuid4().hex[:8]}"

        # Generate session ID if not provided
        if 'session_id' not in feedback_data:
            feedback_data['session_id'] = str(uuid.uuid4())

        # Add timestamp if not provided
        if 'timestamp' not in feedback_data:
            feedback_data['timestamp'] = datetime.now().isoformat()

        if RL_FEEDBACK_AVAILABLE:
            success = collect_user_feedback(feedback_data)
            if success:
                return jsonify({
                    'status': 'success',
                    'message': 'Feedback collected successfully',
                    'feedback_id': feedback_data['feedback_id']
                })
            else:
                return jsonify({'error': 'Failed to store feedback'}), 500
        else:
            return jsonify({'error': 'RL feedback system not available'}), 503

    except Exception as e:
        print(f"Error submitting feedback: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/learning-insights', methods=['GET'])
def get_learning_insights():
    """Get insights from the reinforcement learning system"""
    try:
        if RL_FEEDBACK_AVAILABLE:
            insights = rl_engine.get_learning_insights()
            return jsonify(insights)
        else:
            return jsonify({'error': 'RL feedback system not available'}), 503

    except Exception as e:
        print(f"Error getting learning insights: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'ollama_available': OLLAMA_AVAILABLE,
        'database_available': DATABASE_AVAILABLE,
        'rl_feedback_available': RL_FEEDBACK_AVAILABLE,
        'model': 'llama3.2' if OLLAMA_AVAILABLE else 'fallback'
    })

if __name__ == '__main__':
    print("Starting Flask API server...")
    print(f"Ollama available: {OLLAMA_AVAILABLE}")
    if OLLAMA_AVAILABLE:
        print("Using Ollama model: llama3.2")
    else:
        print("Using fallback rule-based recommendations")
    app.run(debug=True, host='0.0.0.0', port=5001)
