from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from vectors import retriver
from portfolio_optimizer import PortfolioOptimizer, InvestorProfile, OptimizationConstraints
from financial_calculator import FinancialCalculator, RetirementPlan, FinancialGoal
from datetime import datetime, timedelta
import json

model = OllamaLLM(model="llama3.2")

# Enhanced template with portfolio optimization and financial planning
template = """
You are an advanced AI financial planner with access to sophisticated portfolio optimization and financial planning tools.

CONTEXT:
- Relevant financial instruments: {instruments}
- Portfolio optimization results: {portfolio_analysis}
- Financial planning calculations: {financial_projections}
- User profile: Age {age}, 
  Retirement Age {retirement_age}, 
  Annual Income ${annual_income}, 
  Annual Expenses ${annual_expenses}, 
  Current Savings ${current_savings}

USER QUESTION: {question}

INSTRUCTIONS:
1. Provide comprehensive financial advice based on the user's profile and goals
2. Include specific portfolio recommendations with asset allocations
3. Show detailed financial projections and timelines
4. Explain the reasoning behind your recommendations
5. Include risk assessment and alternative scenarios
6. Format your response professionally with clear sections
7. Be specific with numbers and percentages
8. Provide actionable steps for the user to follow if in case goal amount falls short
   in given time frame and provide alternative portfolio recommendations

Your response should include:
- Executive Summary
- Portfolio Recommendations
- Financial Projections
- Risk Analysis
- Action Steps
- Recommend WIO Personal App, WIO Invest App for Investment Options
"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

def get_user_input():
    """Collect comprehensive user information"""
    print("\n" + "="*50)
    print("🏦 ADVANCED FINANCIAL PLANNER AI")
    print("="*50)

    user_data = {}

    # Basic information
    user_data['age'] = int(input("What is your current age? "))
    user_data['retirement_age'] = int(input("At what age do you plan to retire? "))
    user_data['annual_income'] = float(input("What is your annual income ($)? "))
    user_data['annual_expenses'] = float(input("What are your annual expenses ($)? "))
    user_data['current_savings'] = float(input("What are your current savings ($)? "))

    # Risk and preferences
    print("\nRisk Tolerance (1-10 scale):")
    print("1-3: Conservative, 4-6: Moderate, 7-10: Aggressive")
    user_data['risk_tolerance'] = int(input("Your risk tolerance (1-10): "))

    user_data['sharia_compliant'] = input("Do you prefer Sharia-compliant investments? (y/n): ").lower() == 'y'

    market_pref = input("Market preference (UAE/US/Both): ").upper()
    user_data['market_preference'] = market_pref if market_pref in ['UAE', 'US'] else None

    return user_data

def analyze_portfolio_and_finances(user_data, question):
    """Perform comprehensive financial analysis"""

    # Create investor profile
    investor_profile = InvestorProfile(
        age=user_data['age'],
        retirement_age=user_data['retirement_age'],
        annual_income=user_data['annual_income'],
        annual_expenses=user_data['annual_expenses'],
        current_savings=user_data['current_savings'],
        risk_tolerance=user_data['risk_tolerance'],
        investment_horizon=user_data['retirement_age'] - user_data['age'],
        financial_goals=["Retirement Planning"],
        sharia_compliant=user_data['sharia_compliant']
    )

    # Create optimization constraints
    constraints = OptimizationConstraints(
        sharia_compliant_only=user_data['sharia_compliant'],
        market_preference=user_data['market_preference'],
        risk_level_range=(max(1, user_data['risk_tolerance']-2),
                         min(10, user_data['risk_tolerance']+2))
    )

    # Portfolio optimization with enhanced error handling
    optimizer = PortfolioOptimizer()
    portfolio_analysis = "Portfolio optimization not available"

    try:
        # First check if we have sufficient data
        from investment_database import InvestmentDatabase
        test_db = InvestmentDatabase()
        summary = test_db.get_data_summary()
        test_db.close()

        if summary['total_data_points'] < 1000:
            portfolio_analysis = """
            PORTFOLIO ANALYSIS UNAVAILABLE:
            - Insufficient historical data for optimization
            - Please run: python refresh_database.py
            - This will generate enhanced historical data for better analysis

            GENERAL RECOMMENDATIONS BASED ON PROFILE:
            """
            # Provide basic recommendations based on risk tolerance
            if user_data['risk_tolerance'] <= 3:
                portfolio_analysis += "\n        - Conservative allocation: 30% Stocks, 60% Bonds, 10% Cash"
                portfolio_analysis += "\n        - Focus on UAE government bonds and stable banking stocks"
            elif user_data['risk_tolerance'] <= 6:
                portfolio_analysis += "\n        - Moderate allocation: 50% Stocks, 45% Bonds, 5% Cash"
                portfolio_analysis += "\n        - Mix of UAE and US ETFs for diversification"
            else:
                portfolio_analysis += "\n        - Aggressive allocation: 70% Stocks, 25% Bonds, 5% Cash"
                portfolio_analysis += "\n        - Growth-focused with international exposure"
        else:
            # Proceed with optimization
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

            portfolio_analysis += f"\n\n        RECOMMENDATION: This optimized portfolio is based on {summary['total_data_points']:,} data points"

    except Exception as e:
        portfolio_analysis = f"""
        PORTFOLIO OPTIMIZATION TEMPORARILY UNAVAILABLE:
        - Error: {str(e)}
        - Suggestion: Run 'python refresh_database.py' to update data

        BASIC RECOMMENDATIONS FOR YOUR PROFILE:
        - Risk Tolerance: {user_data['risk_tolerance']}/10
        - Investment Horizon: {user_data['retirement_age'] - user_data['age']} years
        """
        if user_data['sharia_compliant']:
            portfolio_analysis += "\n        - Focus on Sharia-compliant instruments available in database"
        if user_data['market_preference']:
            portfolio_analysis += f"\n        - Preferred market: {user_data['market_preference']}"
    finally:
        optimizer.close()

    # Financial planning calculations
    calculator = FinancialCalculator()

    retirement_plan = RetirementPlan(
        current_age=user_data['age'],
        retirement_age=user_data['retirement_age'],
        current_savings=user_data['current_savings'],
        monthly_contribution=(user_data['annual_income'] - user_data['annual_expenses']) / 12,
        expected_return=0.08
    )

    retirement_analysis = calculator.calculate_retirement_needs(retirement_plan, user_data['annual_income'])

    financial_projections = f"""
    RETIREMENT PLANNING ANALYSIS:
    - Retirement Corpus Needed: ${retirement_analysis['retirement_corpus_needed']:,.0f}
    - Current Path Total: ${retirement_analysis['total_accumulated']:,.0f}
    - Shortfall: ${retirement_analysis['shortfall']:,.0f}
    - Additional Monthly Savings Needed: ${retirement_analysis['required_additional_monthly_savings']:,.0f}
    - On Track: {'Yes' if retirement_analysis['is_on_track'] else 'No'}
    """

    return portfolio_analysis, financial_projections

def main():
    """Main application loop"""
    while True:
        print("\n" + "="*60)
        question = input("💭 Share your financial goals and questions (or 'q' to quit): ")

        if question.lower() == 'q':
            print("Thank you for using the Financial Planner AI! 👋")
            break

        # Get user information
        user_data = get_user_input()

        print("\n🔄 Analyzing your financial situation...")

        # Get relevant instruments from vector database
        instruments = retriver.invoke(question)

        # Perform comprehensive analysis
        portfolio_analysis, financial_projections = analyze_portfolio_and_finances(user_data, question)

        # Generate AI response
        result = chain.invoke({
            "instruments": instruments,
            "portfolio_analysis": portfolio_analysis,
            "financial_projections": financial_projections,
            "question": question,
            "age": user_data['age'],
            "retirement_age": user_data['retirement_age'],
            "annual_income": user_data['annual_income'],
            "annual_expenses": user_data['annual_expenses'],
            "current_savings": user_data['current_savings']
        })

        print("\n" + "="*60)
        print("📊 COMPREHENSIVE FINANCIAL ANALYSIS")
        print("="*60)
        print(result)
        print("="*60)

if __name__ == "__main__":
    main()