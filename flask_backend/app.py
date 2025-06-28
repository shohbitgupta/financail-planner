#!/usr/bin/env python3
"""
Flask Backend for Financial Planner AI Web App

This backend connects the Flutter web app with your existing financial planner AI agent.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
from datetime import datetime

# Add the parent directory to path to import your existing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from portfolio_optimizer import PortfolioOptimizer, InvestorProfile, OptimizationConstraints
    from financial_calculator import FinancialCalculator, RetirementPlan
    from investment_database import InvestmentDatabase
except ImportError as e:
    print(f"Warning: Could not import some modules: {e}")
    print("Some features may not work properly.")

app = Flask(__name__)
CORS(app)  # Enable CORS for Flutter web app

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'message': 'Financial Planner AI Backend is running'
    })

@app.route('/api/financial-plan', methods=['POST'])
def get_financial_plan():
    """Main endpoint for financial planning requests"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        user_profile = data.get('user_profile')
        query = data.get('query', '')
        
        if not user_profile:
            return jsonify({'error': 'User profile is required'}), 400
        
        # Create investor profile
        investor_profile = InvestorProfile(
            age=user_profile['age'],
            retirement_age=user_profile['retirement_age'],
            annual_income=user_profile['annual_income'],
            annual_expenses=user_profile['annual_expenses'],
            current_savings=user_profile['current_savings'],
            risk_tolerance=user_profile['risk_tolerance'],
            investment_horizon=user_profile['retirement_age'] - user_profile['age'],
            financial_goals=user_profile.get('financial_goals', ['Retirement']),
            sharia_compliant=user_profile.get('sharia_compliant', False)
        )
        
        # Portfolio optimization
        portfolio_analysis = None
        try:
            constraints = OptimizationConstraints(
                sharia_compliant_only=user_profile.get('sharia_compliant', False),
                market_preference=user_profile.get('market_preference'),
                risk_level_range=(
                    max(1, user_profile['risk_tolerance'] - 2),
                    min(10, user_profile['risk_tolerance'] + 2)
                )
            )
            
            optimizer = PortfolioOptimizer()
            portfolio_result = optimizer.optimize_portfolio(investor_profile, constraints)
            
            portfolio_analysis = {
                'expected_return': portfolio_result['expected_return'],
                'volatility': portfolio_result['volatility'],
                'sharpe_ratio': portfolio_result['sharpe_ratio'],
                'total_assets': portfolio_result['total_assets'],
                'optimization_type': portfolio_result['optimization_type'],
                'allocations': [
                    {
                        'symbol': symbol,
                        'name': details['asset_info']['name'],
                        'weight': details['weight'],
                        'category': details['asset_info']['category'],
                        'market': details['asset_info']['market'],
                        'sharia_compliant': details['asset_info']['is_sharia_compliant']
                    }
                    for symbol, details in portfolio_result['allocation'].items()
                ]
            }
            optimizer.close()
            
        except Exception as e:
            print(f"Portfolio optimization error: {e}")
            # Provide fallback portfolio analysis
            portfolio_analysis = create_fallback_portfolio(user_profile)
        
        # Retirement projection
        calculator = FinancialCalculator()
        retirement_plan = RetirementPlan(
            current_age=user_profile['age'],
            retirement_age=user_profile['retirement_age'],
            current_savings=user_profile['current_savings'],
            monthly_contribution=(user_profile['annual_income'] - user_profile['annual_expenses']) / 12,
            expected_return=0.08
        )
        
        retirement_analysis = calculator.calculate_retirement_needs(retirement_plan, user_profile['annual_income'])
        
        retirement_projection = {
            'retirement_corpus_needed': retirement_analysis['retirement_corpus_needed'],
            'current_path_total': retirement_analysis['total_accumulated'],
            'shortfall': retirement_analysis['shortfall'],
            'additional_monthly_savings_needed': retirement_analysis['required_additional_monthly_savings'],
            'on_track': retirement_analysis['is_on_track'],
            'years_to_retirement': retirement_analysis['years_to_retirement']
        }
        
        # Risk assessment
        risk_assessment = create_risk_assessment(user_profile)
        
        # AI recommendations
        ai_recommendations = generate_ai_recommendations(user_profile, query, portfolio_analysis, retirement_projection)
        
        # Prepare response
        response = {
            'user_profile': user_profile,
            'portfolio_analysis': portfolio_analysis,
            'retirement_projection': retirement_projection,
            'risk_assessment': risk_assessment,
            'ai_recommendations': ai_recommendations,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error in financial plan endpoint: {e}")
        return jsonify({'error': str(e)}), 500

def create_fallback_portfolio(user_profile):
    """Create a fallback portfolio when optimization fails"""
    risk_tolerance = user_profile['risk_tolerance']
    
    # Simple rule-based allocation
    if risk_tolerance <= 3:
        # Conservative
        allocations = [
            {'symbol': 'AGG', 'name': 'US Aggregate Bonds', 'weight': 0.4, 'category': 'Bond', 'market': 'US', 'sharia_compliant': False},
            {'symbol': 'SPY', 'name': 'S&P 500 ETF', 'weight': 0.3, 'category': 'ETF', 'market': 'US', 'sharia_compliant': False},
            {'symbol': 'FAB', 'name': 'First Abu Dhabi Bank', 'weight': 0.2, 'category': 'Banking', 'market': 'UAE', 'sharia_compliant': True},
            {'symbol': 'UAEETF', 'name': 'UAE Equity ETF', 'weight': 0.1, 'category': 'ETF', 'market': 'UAE', 'sharia_compliant': True},
        ]
        expected_return = 0.06
        volatility = 0.12
    elif risk_tolerance <= 6:
        # Moderate
        allocations = [
            {'symbol': 'SPY', 'name': 'S&P 500 ETF', 'weight': 0.35, 'category': 'ETF', 'market': 'US', 'sharia_compliant': False},
            {'symbol': 'VTI', 'name': 'Total Stock Market ETF', 'weight': 0.25, 'category': 'ETF', 'market': 'US', 'sharia_compliant': False},
            {'symbol': 'FAB', 'name': 'First Abu Dhabi Bank', 'weight': 0.15, 'category': 'Banking', 'market': 'UAE', 'sharia_compliant': True},
            {'symbol': 'AGG', 'name': 'US Aggregate Bonds', 'weight': 0.15, 'category': 'Bond', 'market': 'US', 'sharia_compliant': False},
            {'symbol': 'EMAAR', 'name': 'Emaar Properties', 'weight': 0.1, 'category': 'Real Estate', 'market': 'UAE', 'sharia_compliant': True},
        ]
        expected_return = 0.08
        volatility = 0.15
    else:
        # Aggressive
        allocations = [
            {'symbol': 'QQQ', 'name': 'Nasdaq-100 ETF', 'weight': 0.3, 'category': 'ETF', 'market': 'US', 'sharia_compliant': False},
            {'symbol': 'SPY', 'name': 'S&P 500 ETF', 'weight': 0.25, 'category': 'ETF', 'market': 'US', 'sharia_compliant': False},
            {'symbol': 'VTI', 'name': 'Total Stock Market ETF', 'weight': 0.2, 'category': 'ETF', 'market': 'US', 'sharia_compliant': False},
            {'symbol': 'EMAAR', 'name': 'Emaar Properties', 'weight': 0.15, 'category': 'Real Estate', 'market': 'UAE', 'sharia_compliant': True},
            {'symbol': 'FAB', 'name': 'First Abu Dhabi Bank', 'weight': 0.1, 'category': 'Banking', 'market': 'UAE', 'sharia_compliant': True},
        ]
        expected_return = 0.12
        volatility = 0.20
    
    return {
        'expected_return': expected_return,
        'volatility': volatility,
        'sharpe_ratio': (expected_return - 0.02) / volatility,
        'total_assets': len(allocations),
        'optimization_type': 'rule_based',
        'allocations': allocations
    }

def create_risk_assessment(user_profile):
    """Create risk assessment based on user profile"""
    risk_score = user_profile['risk_tolerance']
    
    if risk_score <= 2:
        risk_category = 'Conservative'
    elif risk_score <= 4:
        risk_category = 'Moderate Conservative'
    elif risk_score <= 6:
        risk_category = 'Moderate'
    elif risk_score <= 8:
        risk_category = 'Moderate Aggressive'
    else:
        risk_category = 'Aggressive'
    
    return {
        'risk_score': risk_score,
        'risk_category': risk_category,
        'time_horizon': user_profile['retirement_age'] - user_profile['age'],
        'financial_capacity': 'Medium',
        'behavioral_traits': {
            'loss_tolerance': 'Moderate - Can handle some volatility',
            'monitoring_style': 'Passive - Long-term focused approach',
            'experience_level': 'Intermediate - Has basic knowledge'
        },
        'recommendations': [
            f'Asset Allocation suitable for {risk_category} investor',
            'Regular portfolio rebalancing recommended',
            'Consider dollar-cost averaging for investments',
            'Monitor progress annually'
        ]
    }

def generate_ai_recommendations(user_profile, query, portfolio_analysis, retirement_projection):
    """Generate AI-powered recommendations"""

    # Include user query context if provided
    query_context = f"\n## Your Question: {query}\n" if query and query.strip() else ""

    recommendations = f"""
## Executive Summary
Based on your profile (Age: {user_profile['age']}, Risk Tolerance: {user_profile['risk_tolerance']}/10), you have {user_profile['retirement_age'] - user_profile['age']} years until retirement.{query_context}

## Portfolio Recommendations
- **Expected Return**: {portfolio_analysis['expected_return']:.1%} annually
- **Risk Level**: {portfolio_analysis['volatility']:.1%} volatility
- **Diversification**: {portfolio_analysis['total_assets']} different assets
- **Sharia Compliance**: {'Yes' if user_profile.get('sharia_compliant') else 'Mixed conventional and Islamic instruments'}

## Financial Projections
- **Retirement Status**: {'✅ On Track' if retirement_projection['on_track'] else '⚠️ Needs Attention'}
- **Required Corpus**: ${retirement_projection['retirement_corpus_needed']:,.0f}
- **Current Path**: ${retirement_projection['current_path_total']:,.0f}

## Action Steps
1. Implement the recommended portfolio allocation
2. {'Continue current savings rate' if retirement_projection['on_track'] else f'Increase monthly savings by ${retirement_projection["additional_monthly_savings_needed"]:,.0f}'}
3. Review and rebalance portfolio quarterly
4. Monitor progress annually
5. Consider tax-advantaged investment accounts

## Market Focus
- **UAE Market**: Strong banking and real estate sectors
- **US Market**: Technology and broad market exposure
- **Currency**: Diversification across AED and USD
    """
    
    return recommendations.strip()

@app.route('/api/instruments', methods=['GET'])
def get_instruments():
    """Get available investment instruments"""
    try:
        db = InvestmentDatabase()
        instruments = db.get_all_instruments()
        db.close()
        
        return jsonify({
            'instruments': instruments.to_dict('records'),
            'total_count': len(instruments)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Financial Planner AI Backend...")
    print("📊 Backend will be available at: http://localhost:8000")
    print("🌐 Flutter web app should connect to this endpoint")
    
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True
    )
