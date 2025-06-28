from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import sys
import os
import re

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from vectors import retriver
    VECTORS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import vectors module: {e}")
    VECTORS_AVAILABLE = False
    retriver = None

try:
    from portfolio_optimizer import PortfolioOptimizer, InvestorProfile, OptimizationConstraints
    PORTFOLIO_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import portfolio_optimizer: {e}")
    PORTFOLIO_AVAILABLE = False

try:
    from financial_calculator import FinancialCalculator, RetirementPlan
    FINANCIAL_CALC_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import financial_calculator: {e}")
    FINANCIAL_CALC_AVAILABLE = False

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize Ollama model
model = OllamaLLM(model="llama3.2")

# Enhanced template for structured financial planning
template = """
You are an advanced AI financial planner. Based on the provided analysis, create a comprehensive financial plan.

USER PROFILE:
- Age: {age}
- Retirement Age: {retirement_age}
- Annual Income: ${annual_income:,.0f}
- Annual Expenses: ${annual_expenses:,.0f}
- Current Savings: ${current_savings:,.0f}
- Risk Tolerance: {risk_tolerance}/10
- Investment Goals: {goals}
- Sharia Compliant: {is_sharia_compliant}
- Preferred Market: {preferred_market}

PORTFOLIO ANALYSIS:
{portfolio_analysis}

FINANCIAL PROJECTIONS:
{financial_projections}

RELEVANT INSTRUMENTS:
{instruments}

Please provide a structured response with the following sections:

1. EXECUTIVE SUMMARY (2-3 sentences)

2. PORTFOLIO RECOMMENDATIONS (List 3-5 specific investments with allocation percentages)

3. RISK ASSESSMENT (Brief analysis of portfolio risk level)

4. TIME HORIZON ANALYSIS (How the investment timeline affects strategy)

5. MONTHLY SAVINGS NEEDED (Specific amount to reach goals)

6. GOAL ACHIEVEMENT TIMELINE (When each goal can be achieved)

7. ADDITIONAL ADVICE (3-4 actionable recommendations)

8. COMPLIANCE NOTES (If Sharia compliance is required)

Keep responses professional, specific with numbers, and actionable.
"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

def analyze_portfolio_and_finances(user_data):
    """Perform comprehensive financial analysis using existing modules"""

    portfolio_analysis = "Portfolio optimization not available"
    financial_projections = "Financial projections not available"

    # Create basic analysis even if modules are not available
    risk_map = {'conservative': 3, 'moderate': 6, 'aggressive': 9}
    risk_level = risk_map.get(user_data['risk_tolerance'], 6)

    if PORTFOLIO_AVAILABLE:
        try:
            # Create investor profile
            investor_profile = InvestorProfile(
                age=user_data['age'],
                retirement_age=user_data['retirement_age'],
                annual_income=user_data['annual_salary'],
                annual_expenses=user_data['annual_expenses'],
                current_savings=user_data['current_savings'],
                risk_tolerance=risk_level,
                investment_horizon=user_data['retirement_age'] - user_data['age'],
                financial_goals=user_data['goals'],
                sharia_compliant=user_data['is_sharia_compliant']
            )

            # Create optimization constraints
            constraints = OptimizationConstraints(
                sharia_compliant_only=user_data['is_sharia_compliant'],
                market_preference=user_data['preferred_market'] if user_data['preferred_market'] != 'BOTH' else None,
                risk_level_range=(max(1, risk_level-2), min(10, risk_level+2))
            )

            # Portfolio optimization
            optimizer = PortfolioOptimizer()
            portfolio_result = optimizer.optimize_portfolio(investor_profile, constraints)

            portfolio_analysis = f"""
            OPTIMAL PORTFOLIO ALLOCATION:
            - Expected Annual Return: {portfolio_result['expected_return']:.1%}
            - Portfolio Volatility: {portfolio_result['volatility']:.1%}
            - Sharpe Ratio: {portfolio_result['sharpe_ratio']:.2f}
            - Number of Assets: {portfolio_result['total_assets']}

            TOP ALLOCATIONS:
            """
            for symbol, details in list(portfolio_result['allocation'].items())[:5]:
                portfolio_analysis += f"\n        - {symbol}: {details['weight']:.1%} ({details['asset_info']['name']})"

            optimizer.close()

        except Exception as e:
            portfolio_analysis = f"""
            PORTFOLIO OPTIMIZATION ERROR:
            - Error: {str(e)}

            BASIC RECOMMENDATIONS FOR YOUR PROFILE:
            - Risk Tolerance: {risk_level}/10
            - Investment Horizon: {user_data['retirement_age'] - user_data['age']} years
            """
    else:
        portfolio_analysis = f"""
        BASIC PORTFOLIO RECOMMENDATIONS:
        - Risk Tolerance: {risk_level}/10
        - Investment Horizon: {user_data['retirement_age'] - user_data['age']} years
        - Recommended allocation based on risk profile
        """
        if user_data['is_sharia_compliant']:
            portfolio_analysis += "\n        - Focus on Sharia-compliant instruments"
        if user_data['preferred_market'] != 'BOTH':
            portfolio_analysis += f"\n        - Preferred market: {user_data['preferred_market']}"

    # Financial planning calculations
    if FINANCIAL_CALC_AVAILABLE:
        try:
            calculator = FinancialCalculator()

            retirement_plan = RetirementPlan(
                current_age=user_data['age'],
                retirement_age=user_data['retirement_age'],
                current_savings=user_data['current_savings'],
                monthly_contribution=(user_data['annual_salary'] - user_data['annual_expenses']) / 12,
                expected_return=0.08
            )

            retirement_analysis = calculator.calculate_retirement_needs(retirement_plan, user_data['annual_salary'])

            financial_projections = f"""
            RETIREMENT PLANNING ANALYSIS:
            - Retirement Corpus Needed: ${retirement_analysis['retirement_corpus_needed']:,.0f}
            - Current Path Total: ${retirement_analysis['total_accumulated']:,.0f}
            - Shortfall: ${retirement_analysis['shortfall']:,.0f}
            - Additional Monthly Savings Needed: ${retirement_analysis['required_additional_monthly_savings']:,.0f}
            - On Track: {'Yes' if retirement_analysis['is_on_track'] else 'No'}
            """

        except Exception as e:
            financial_projections = f"""
            FINANCIAL PROJECTIONS ERROR:
            - Error: {str(e)}
            - Basic calculation: Monthly savings capacity = ${(user_data['annual_salary'] - user_data['annual_expenses'])/12:,.0f}
            """
    else:
        monthly_savings_capacity = (user_data['annual_salary'] - user_data['annual_expenses']) / 12
        years_to_retirement = user_data['retirement_age'] - user_data['age']

        financial_projections = f"""
        BASIC FINANCIAL PROJECTIONS:
        - Monthly savings capacity: ${monthly_savings_capacity:,.0f}
        - Years to retirement: {years_to_retirement}
        - Estimated retirement needs: ${user_data['annual_expenses'] * 20:,.0f} (20x annual expenses)
        - Current savings: ${user_data['current_savings']:,.0f}
        """

    return portfolio_analysis, financial_projections

def parse_llm_response_to_structured_data(llm_response, user_data):
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
    goal_timeline = extract_section(r'GOAL ACHIEVEMENT TIMELINE[:\s]*\n(.*?)(?=\n\d+\.|\n[A-Z]|\Z)', llm_response)
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
                    percentage = float(percentage_match.group(1)) if percentage_match else 10.0
                    
                    recommendations.append({
                        'symbol': name_part[:10],  # Truncate for symbol
                        'name': name_part,
                        'category': 'Investment',
                        'allocation_percentage': percentage,
                        'investment_amount': (user_data.get('monthly_investment', 1000) * percentage / 100),
                        'rationale': details_part,
                        'risk_level': 5,  # Default
                        'expected_return': 0.08,  # Default
                        'market': user_data.get('preferred_market', 'UAE')
                    })
    
    # If no recommendations parsed, create default ones
    if not recommendations:
        recommendations = [
            {
                'symbol': 'BALANCED',
                'name': 'Balanced Portfolio Allocation',
                'category': 'Mixed Assets',
                'allocation_percentage': 100,
                'investment_amount': user_data.get('monthly_investment', 1000),
                'rationale': 'Diversified allocation based on your risk profile',
                'risk_level': 5,
                'expected_return': 0.08,
                'market': user_data.get('preferred_market', 'UAE')
            }
        ]
    
    # Extract monthly savings amount
    monthly_savings_amount = 1000  # Default
    if monthly_savings:
        amount_match = re.search(r'\$?(\d+(?:,\d+)*(?:\.\d+)?)', monthly_savings)
        if amount_match:
            monthly_savings_amount = float(amount_match.group(1).replace(',', ''))
    
    # Parse goals timeline
    goal_achievement_timeline = {}
    if goal_timeline:
        for goal in user_data.get('goals', []):
            # Default timeline based on goal type
            if 'retirement' in goal.lower():
                goal_achievement_timeline[goal] = user_data['retirement_age'] - user_data['age']
            elif 'education' in goal.lower():
                goal_achievement_timeline[goal] = 10
            else:
                goal_achievement_timeline[goal] = 15
    
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
            "Review and rebalance your portfolio annually"
        ]
    
    # Calculate total allocation
    total_allocation = {}
    for rec in recommendations:
        category = rec['category']
        if category in total_allocation:
            total_allocation[category] += rec['allocation_percentage']
        else:
            total_allocation[category] = rec['allocation_percentage']
    
    return {
        'user_profile': {
            'age': user_data['age'],
            'retirement_age': user_data['retirement_age'],
            'annual_income': user_data['annual_salary'],
            'annual_expenses': user_data['annual_expenses'],
            'current_savings': user_data['current_savings'],
            'monthly_investment': user_data.get('monthly_investment', 1000),
            'risk_tolerance': user_data['risk_tolerance'],
            'investment_horizon': user_data['retirement_age'] - user_data['age'],
            'goals': user_data['goals'],
            'is_sharia_compliant': user_data['is_sharia_compliant'],
            'preferred_market': user_data['preferred_market'],
            'currency': user_data.get('currency', 'AED')
        },
        'recommendations': recommendations,
        'total_allocation': total_allocation,
        'risk_assessment': risk_assessment or "Moderate risk portfolio suitable for your profile",
        'time_horizon_analysis': time_horizon or f"{user_data['retirement_age'] - user_data['age']}-year horizon allows for balanced growth strategy",
        'expected_portfolio_return': 0.08,  # Default 8%
        'monthly_savings_needed': monthly_savings_amount,
        'goal_achievement_timeline': goal_achievement_timeline,
        'additional_advice': advice_list,
        'compliance_notes': compliance_notes or ("Sharia-compliant investments selected" if user_data['is_sharia_compliant'] else ""),
        'executive_summary': executive_summary or "Comprehensive financial plan created based on your profile and goals"
    }

@app.route('/api/generate-financial-plan', methods=['POST'])
def generate_financial_plan():
    """Generate financial plan using Ollama LLM"""
    try:
        user_data = request.json
        
        # Validate required fields
        required_fields = ['age', 'retirement_age', 'annual_salary', 'annual_expenses', 'current_savings']
        for field in required_fields:
            if field not in user_data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        print(f"Received user data: {user_data}")
        
        # Get relevant instruments from vector database
        if VECTORS_AVAILABLE and retriver:
            try:
                question = f"Investment recommendations for {user_data.get('goals', ['retirement'])} with {user_data.get('risk_tolerance', 'moderate')} risk tolerance"
                instruments = retriver.invoke(question)
            except Exception as e:
                print(f"Vector retrieval error: {e}")
                instruments = "UAE and US market instruments available for diversified portfolio allocation"
        else:
            instruments = "UAE and US market instruments available for diversified portfolio allocation"
        
        # Perform comprehensive analysis
        portfolio_analysis, financial_projections = analyze_portfolio_and_finances(user_data)
        
        # Generate AI response using Ollama
        llm_response = chain.invoke({
            'age': user_data['age'],
            'retirement_age': user_data['retirement_age'],
            'annual_income': user_data['annual_salary'],
            'annual_expenses': user_data['annual_expenses'],
            'current_savings': user_data['current_savings'],
            'risk_tolerance': user_data.get('risk_tolerance', 'moderate'),
            'goals': ', '.join(user_data.get('goals', [])),
            'is_sharia_compliant': 'Yes' if user_data.get('is_sharia_compliant', False) else 'No',
            'preferred_market': user_data.get('preferred_market', 'UAE'),
            'portfolio_analysis': portfolio_analysis,
            'financial_projections': financial_projections,
            'instruments': instruments
        })
        
        print(f"LLM Response: {llm_response}")
        
        # Parse LLM response into structured data
        structured_plan = parse_llm_response_to_structured_data(llm_response, user_data)
        
        # Add the raw LLM response for debugging
        structured_plan['raw_llm_response'] = llm_response
        
        return jsonify(structured_plan)
        
    except Exception as e:
        print(f"Error generating financial plan: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'model': 'llama3.2'})

if __name__ == '__main__':
    print("Starting Flask API server...")
    print("Ollama model: llama3.2")
    app.run(debug=True, host='0.0.0.0', port=5000)
