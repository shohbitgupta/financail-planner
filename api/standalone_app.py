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
    if category.lower() in ['equity', 'stock', 'etf'] or 'stock' in category.lower():
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
    elif category.lower() in ['bond', 'fixed income', 'savings'] or any(term in category.lower() for term in ['bond', 'fixed', 'saving']):
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
            'app_name': 'WIO Banking App',
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

# Enhanced template for structured financial planning with vector context
template = """
You are an advanced AI financial planner with access to comprehensive market data and historical analysis.

RELEVANT MARKET CONTEXT:
{instruments}

USER PROFILE:
- Age: {age}
- Retirement Age: {retirement_age}
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

Please provide a structured response with the following sections:

1. EXECUTIVE SUMMARY (2-3 sentences about the overall financial situation)
2. PORTFOLIO RECOMMENDATIONS (List 3-5 specific investments with allocation percentages)
3. RISK ASSESSMENT (Brief analysis of portfolio risk level based on user profile)
4. TIME HORIZON ANALYSIS (How the investment timeline affects strategy)
5. MONTHLY SAVINGS NEEDED (Specific amount to reach retirement goals)
6. GOAL ACHIEVEMENT TIMELINE (When each goal can be achieved)
7. ADDITIONAL ADVICE (3-4 actionable recommendations)
8. COMPLIANCE NOTES (If Sharia compliance is required, mention suitable instruments)

Keep responses professional, specific with numbers, and actionable. Focus on UAE and US market opportunities.
"""

prompt = ChatPromptTemplate.from_template(template)

def clean_nan_values(value):
    """Convert NaN values to None for JSON serialization"""
    import math
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    return value

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

def parse_llm_response_to_structured_data(llm_response, user_data, financial_metrics):
    """Parse LLM response into structured data for React UI"""
    
    # Extract sections using regex patterns
    def extract_section(pattern, text):
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else ""
    
    # Parse different sections
    executive_summary = extract_section(r'EXECUTIVE SUMMARY[:\s]*\n(.*?)(?=\n\d+\.|\n[A-Z]|\Z)', llm_response)
    portfolio_recommendations = extract_section(r'PORTFOLIO RECOMMENDATIONS[:\s]*\n(.*?)(?=\n\d+\.|\n[A-Z]|\Z)', llm_response)
    risk_assessment = extract_section(r'RISK ASSESSMENT[:\s]*\n(.*?)(?=\n\d+\.|\n[A-Z]|\Z)', llm_response)
    time_horizon = extract_section(r'TIME HORIZON ANALYSIS[:\s]*\n(.*?)(?=\n\d+\.|\n[A-Z]|\Z)', llm_response)
    monthly_savings = extract_section(r'MONTHLY SAVINGS NEEDED[:\s]*\n(.*?)(?=\n\d+\.|\n[A-Z]|\Z)', llm_response)
    # goal_timeline = extract_section(r'GOAL ACHIEVEMENT TIMELINE[:\s]*\n(.*?)(?=\n\d+\.|\n[A-Z]|\Z)', llm_response)  # Not used - we create structured timeline below
    additional_advice = extract_section(r'ADDITIONAL ADVICE[:\s]*\n(.*?)(?=\n\d+\.|\n[A-Z]|\Z)', llm_response)
    compliance_notes = extract_section(r'COMPLIANCE NOTES[:\s]*\n(.*?)(?=\n\d+\.|\n[A-Z]|\Z)', llm_response)
    
    # Parse portfolio recommendations into structured format
    recommendations = []
    if portfolio_recommendations:
        lines = portfolio_recommendations.split('\n')
        for line in lines:
            if '-' in line and '%' in line:
                # Extract investment details
                parts = line.strip('- ').split(':')
                if len(parts) >= 2:
                    name_part = parts[0].strip()
                    details_part = parts[1].strip()
                    
                    # Extract percentage
                    percentage_match = re.search(r'(\d+(?:\.\d+)?)%', details_part)
                    percentage = float(percentage_match.group(1)) if percentage_match else 20.0
                    
                    # Determine category based on name
                    category = 'Investment'
                    if any(keyword in name_part.lower() for keyword in ['stock', 'equity', 'etf']):
                        category = 'Equity'
                    elif any(keyword in name_part.lower() for keyword in ['bond', 'fixed', 'saving']):
                        category = 'Fixed Income'
                    elif any(keyword in name_part.lower() for keyword in ['reit', 'real estate']):
                        category = 'Real Estate'

                    recommendations.append({
                        'symbol': name_part[:10],  # Truncate for symbol
                        'name': name_part,
                        'category': category,
                        'allocation_percentage': percentage,
                        'investment_amount': (financial_metrics['monthly_savings_capacity'] * percentage / 100),
                        'rationale': details_part,
                        'risk_level': 5,  # Default
                        'expected_return': 0.08,  # Default
                        'market': user_data.get('preferred_market', 'UAE'),
                        'platform_recommendation': get_wio_platform_recommendation(category, user_data.get('preferred_market', 'UAE'))
                    })
    
    # Get specific instrument recommendations from database
    specific_recommendations = get_specific_instrument_recommendations(user_data)

    # If we have specific recommendations, use them; otherwise use parsed or fallback
    if specific_recommendations:
        recommendations = specific_recommendations

        # Assign allocations based on risk profile
        risk_map = {'conservative': 3, 'moderate': 6, 'aggressive': 9}
        risk_level = risk_map.get(user_data['risk_tolerance'], 6)

        # Define allocation strategy based on risk level
        if risk_level <= 4:  # Conservative
            allocations = {'Fixed Income': 60, 'Equity': 30, 'Real Estate': 10}
        elif risk_level <= 7:  # Moderate
            allocations = {'Equity': 50, 'Fixed Income': 35, 'Real Estate': 15}
        else:  # Aggressive
            allocations = {'Equity': 70, 'Fixed Income': 20, 'Real Estate': 10}

        # Assign allocations to recommendations
        monthly_capacity = financial_metrics.get('monthly_savings_capacity', 3000)
        for rec in recommendations:
            category = rec['category']
            if category in allocations:
                rec['allocation_percentage'] = allocations[category]
                rec['investment_amount'] = monthly_capacity * (allocations[category] / 100)

    # If no recommendations available, create fallback ones
    elif not recommendations:
        risk_map = {'conservative': 3, 'moderate': 6, 'aggressive': 9}
        risk_level = risk_map.get(user_data['risk_tolerance'], 6)

        if risk_level <= 4:  # Conservative
            recommendations = [
                {'symbol': 'BONDS', 'name': 'Government Bonds', 'category': 'Fixed Income', 'allocation_percentage': 60, 'investment_amount': financial_metrics['monthly_savings_capacity'] * 0.6, 'rationale': 'Stable income with low risk', 'risk_level': 2, 'expected_return': 0.04, 'market': user_data.get('preferred_market', 'UAE')},
                {'symbol': 'EQUITY', 'name': 'Blue Chip Stocks', 'category': 'Equity', 'allocation_percentage': 30, 'investment_amount': financial_metrics['monthly_savings_capacity'] * 0.3, 'rationale': 'Stable dividend-paying companies', 'risk_level': 4, 'expected_return': 0.07, 'market': user_data.get('preferred_market', 'UAE')},
                {'symbol': 'CASH', 'name': 'Money Market', 'category': 'Cash', 'allocation_percentage': 10, 'investment_amount': financial_metrics['monthly_savings_capacity'] * 0.1, 'rationale': 'Emergency fund and liquidity', 'risk_level': 1, 'expected_return': 0.02, 'market': user_data.get('preferred_market', 'UAE')}
            ]
        elif risk_level <= 7:  # Moderate
            recommendations = [
                {'symbol': 'EQUITY', 'name': 'Diversified Equity Fund', 'category': 'Equity', 'allocation_percentage': 50, 'investment_amount': financial_metrics['monthly_savings_capacity'] * 0.5, 'rationale': 'Balanced growth potential', 'risk_level': 5, 'expected_return': 0.08, 'market': user_data.get('preferred_market', 'UAE')},
                {'symbol': 'BONDS', 'name': 'Corporate Bonds', 'category': 'Fixed Income', 'allocation_percentage': 35, 'investment_amount': financial_metrics['monthly_savings_capacity'] * 0.35, 'rationale': 'Steady income with moderate risk', 'risk_level': 3, 'expected_return': 0.05, 'market': user_data.get('preferred_market', 'UAE')},
                {'symbol': 'REIT', 'name': 'Real Estate Investment Trust', 'category': 'Real Estate', 'allocation_percentage': 15, 'investment_amount': financial_metrics['monthly_savings_capacity'] * 0.15, 'rationale': 'Diversification and inflation hedge', 'risk_level': 4, 'expected_return': 0.07, 'market': user_data.get('preferred_market', 'UAE')}
            ]
        else:  # Aggressive
            recommendations = [
                {'symbol': 'GROWTH', 'name': 'Growth Stocks', 'category': 'Equity', 'allocation_percentage': 70, 'investment_amount': financial_metrics['monthly_savings_capacity'] * 0.7, 'rationale': 'High growth potential for long-term wealth building', 'risk_level': 7, 'expected_return': 0.10, 'market': user_data.get('preferred_market', 'UAE')},
                {'symbol': 'INTL', 'name': 'International Equity', 'category': 'Equity', 'allocation_percentage': 20, 'investment_amount': financial_metrics['monthly_savings_capacity'] * 0.2, 'rationale': 'Global diversification', 'risk_level': 6, 'expected_return': 0.09, 'market': 'US'},
                {'symbol': 'BONDS', 'name': 'High-Yield Bonds', 'category': 'Fixed Income', 'allocation_percentage': 10, 'investment_amount': financial_metrics['monthly_savings_capacity'] * 0.1, 'rationale': 'Higher income potential', 'risk_level': 5, 'expected_return': 0.06, 'market': user_data.get('preferred_market', 'UAE')}
            ]
    
    # Calculate total allocation
    total_allocation = {}
    for rec in recommendations:
        category = rec['category']
        if category in total_allocation:
            total_allocation[category] += rec['allocation_percentage']
        else:
            total_allocation[category] = rec['allocation_percentage']
    
    # Parse additional advice into list
    advice_list = []
    if additional_advice:
        lines = additional_advice.split('\n')
        for line in lines:
            if line.strip() and (line.strip().startswith('-') or line.strip().startswith('•')):
                advice_list.append(line.strip('- •').strip())
    
    if not advice_list:
        advice_list = [
            "Start investing early to benefit from compound growth",
            "Diversify your portfolio across different asset classes",
            "Review and rebalance your portfolio annually",
            "Consider tax-efficient investment vehicles"
        ]

    # Create structured goal achievement timeline
    goal_achievement_timeline = {}
    user_goals = user_data.get('goals', ['retirement'])
    investment_horizon = financial_metrics['investment_horizon']

    for goal in user_goals:
        if goal.lower() == 'retirement':
            goal_achievement_timeline[goal] = investment_horizon
        elif goal.lower() in ['house_purchase', 'education']:
            # Shorter term goals
            goal_achievement_timeline[goal] = min(10, investment_horizon)
        elif goal.lower() in ['wealth_building', 'emergency_fund']:
            # Medium term goals
            goal_achievement_timeline[goal] = min(15, investment_horizon)
        elif goal.lower() == 'travel':
            # Short term goal
            goal_achievement_timeline[goal] = min(5, investment_horizon)
        else:
            # Default timeline
            goal_achievement_timeline[goal] = min(12, investment_horizon)

    # If no goals specified, add retirement as default
    if not goal_achievement_timeline:
        goal_achievement_timeline['retirement'] = investment_horizon

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
        'expected_portfolio_return': sum(rec['expected_return'] * rec['allocation_percentage']/100 for rec in recommendations),
        'monthly_savings_needed': financial_metrics['additional_monthly_needed'],
        'goal_achievement_timeline': goal_achievement_timeline,
        'additional_advice': advice_list,
        'compliance_notes': compliance_notes or ("Sharia-compliant investments recommended" if user_data['is_sharia_compliant'] else ""),
        'executive_summary': executive_summary or f"Based on your profile, you need ${financial_metrics['additional_monthly_needed']:,.0f} additional monthly savings to meet your retirement goals",
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

        return jsonify(structured_plan)
        
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
