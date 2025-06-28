#!/usr/bin/env python3
"""
Enhanced Financial Planner AI Agent - Comprehensive Demo

This script demonstrates the advanced capabilities of the financial planner AI agent
including portfolio optimization, financial planning calculations, and risk assessment.
"""

import sys
import os
from datetime import datetime, timedelta

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from investment_database import InvestmentDatabase
from portfolio_optimizer import PortfolioOptimizer, InvestorProfile, OptimizationConstraints
from financial_calculator import FinancialCalculator, RetirementPlan, FinancialGoal
from risk_assessment import RiskAssessment

def demo_database():
    """Demonstrate investment database capabilities"""
    print("\n" + "="*60)
    print("📊 INVESTMENT DATABASE DEMO")
    print("="*60)
    
    db = InvestmentDatabase()
    
    # Show database statistics
    all_instruments = db.get_all_instruments()
    print(f"Total instruments in database: {len(all_instruments)}")
    
    # Show market breakdown
    uae_instruments = db.get_instruments_by_market('UAE')
    us_instruments = db.get_instruments_by_market('US')
    print(f"UAE instruments: {len(uae_instruments)}")
    print(f"US instruments: {len(us_instruments)}")
    
    # Show Sharia-compliant options
    sharia_instruments = db.get_sharia_compliant_instruments()
    print(f"Sharia-compliant instruments: {len(sharia_instruments)}")
    
    # Show sample instruments
    print("\nSample UAE Instruments:")
    print(uae_instruments[['symbol', 'name', 'category', 'risk_level']].head())
    
    print("\nSample US Instruments:")
    print(us_instruments[['symbol', 'name', 'category', 'risk_level']].head())
    
    db.close()

def demo_portfolio_optimization():
    """Demonstrate portfolio optimization capabilities"""
    print("\n" + "="*60)
    print("🎯 PORTFOLIO OPTIMIZATION DEMO")
    print("="*60)
    
    # Create sample investor profiles
    profiles = [
        {
            "name": "Conservative Investor (Age 55)",
            "profile": InvestorProfile(
                age=55, retirement_age=65, annual_income=80000, annual_expenses=60000,
                current_savings=200000, risk_tolerance=3, investment_horizon=10,
                financial_goals=["Retirement"], sharia_compliant=False
            ),
            "constraints": OptimizationConstraints(
                risk_level_range=(1, 5), max_single_asset=0.2
            )
        },
        {
            "name": "Aggressive Young Investor (Age 25)",
            "profile": InvestorProfile(
                age=25, retirement_age=65, annual_income=60000, annual_expenses=40000,
                current_savings=10000, risk_tolerance=8, investment_horizon=40,
                financial_goals=["Retirement", "House"], sharia_compliant=False
            ),
            "constraints": OptimizationConstraints(
                risk_level_range=(5, 10), max_single_asset=0.3
            )
        },
        {
            "name": "Sharia-Compliant Investor (Age 35)",
            "profile": InvestorProfile(
                age=35, retirement_age=60, annual_income=100000, annual_expenses=70000,
                current_savings=50000, risk_tolerance=6, investment_horizon=25,
                financial_goals=["Retirement"], sharia_compliant=True
            ),
            "constraints": OptimizationConstraints(
                sharia_compliant_only=True, risk_level_range=(3, 8)
            )
        }
    ]
    
    optimizer = PortfolioOptimizer()
    
    for profile_data in profiles:
        print(f"\n--- {profile_data['name']} ---")
        
        try:
            result = optimizer.optimize_portfolio(
                profile_data['profile'], 
                profile_data['constraints'], 
                'max_sharpe'
            )
            
            print(f"Expected Return: {result['expected_return']:.1%}")
            print(f"Volatility: {result['volatility']:.1%}")
            print(f"Sharpe Ratio: {result['sharpe_ratio']:.2f}")
            print(f"Number of Assets: {result['total_assets']}")
            
            print("Top 3 Allocations:")
            for i, (symbol, details) in enumerate(list(result['allocation'].items())[:3]):
                print(f"  {i+1}. {symbol}: {details['weight']:.1%} - {details['asset_info']['name']}")
                
        except Exception as e:
            print(f"Optimization failed: {e}")
    
    optimizer.close()

def demo_financial_planning():
    """Demonstrate financial planning calculations"""
    print("\n" + "="*60)
    print("💰 FINANCIAL PLANNING DEMO")
    print("="*60)
    
    calculator = FinancialCalculator()
    
    # Retirement planning scenarios
    scenarios = [
        {
            "name": "Early Career (Age 25)",
            "plan": RetirementPlan(
                current_age=25, retirement_age=65, current_savings=5000,
                monthly_contribution=500, expected_return=0.08
            ),
            "income": 50000
        },
        {
            "name": "Mid Career (Age 40)",
            "plan": RetirementPlan(
                current_age=40, retirement_age=65, current_savings=100000,
                monthly_contribution=1200, expected_return=0.07
            ),
            "income": 80000
        },
        {
            "name": "Late Career (Age 55)",
            "plan": RetirementPlan(
                current_age=55, retirement_age=65, current_savings=300000,
                monthly_contribution=2000, expected_return=0.06
            ),
            "income": 100000
        }
    ]
    
    for scenario in scenarios:
        print(f"\n--- {scenario['name']} ---")
        
        result = calculator.calculate_retirement_needs(scenario['plan'], scenario['income'])
        
        print(f"Retirement Corpus Needed: ${result['retirement_corpus_needed']:,.0f}")
        print(f"Projected Total Savings: ${result['total_accumulated']:,.0f}")
        print(f"Shortfall: ${result['shortfall']:,.0f}")
        print(f"Additional Monthly Savings Needed: ${result['required_additional_monthly_savings']:,.0f}")
        print(f"On Track: {'✅ Yes' if result['is_on_track'] else '❌ No'}")
    
    # Goal planning example
    print(f"\n--- Goal Planning Example ---")
    house_goal = FinancialGoal(
        name="House Down Payment",
        target_amount=100000,
        target_date=datetime(2030, 1, 1),
        priority=1
    )
    
    goal_result = calculator.calculate_goal_funding(house_goal, 20000, 800)
    print(f"Goal: {goal_result['goal_name']}")
    print(f"Target Amount: ${goal_result['target_amount']:,.0f}")
    print(f"Years to Goal: {goal_result['years_to_goal']}")
    print(f"Required Monthly Savings: ${goal_result['required_monthly_savings']:,.0f}")
    print(f"Success Probability: {goal_result['probability_of_success']:.1%}")
    
    # Monte Carlo simulation
    print(f"\n--- Monte Carlo Simulation ---")
    mc_plan = RetirementPlan(
        current_age=30, retirement_age=65, current_savings=50000,
        monthly_contribution=1000, expected_return=0.08
    )
    
    mc_result = calculator.monte_carlo_retirement_simulation(mc_plan, 70000, 100)
    print(f"Success Rate: {mc_result['success_rate']:.1%}")
    print(f"Recommendation: {mc_result['recommendation']}")

def demo_risk_assessment():
    """Demonstrate risk assessment capabilities"""
    print("\n" + "="*60)
    print("🎯 RISK ASSESSMENT DEMO")
    print("="*60)
    
    # Import and run the demo from risk_assessment module
    from risk_assessment import demo_risk_assessment
    demo_risk_assessment()

def demo_query_examples():
    """Show example queries for different investor profiles"""
    print("\n" + "="*60)
    print("💬 EXAMPLE QUERIES FOR DIFFERENT PROFILES")
    print("="*60)
    
    examples = [
        {
            "profile": "Young Professional (Age 28)",
            "queries": [
                "I want to start investing for retirement with $500/month",
                "How should I allocate between UAE and US markets?",
                "I'm planning to buy a house in 5 years, need $80,000 down payment",
                "What's the best strategy for aggressive growth?"
            ]
        },
        {
            "profile": "Mid-Career Executive (Age 45)",
            "queries": [
                "I have $200,000 to invest, need balanced growth and income",
                "How can I optimize my portfolio for tax efficiency?",
                "I want to retire early at 60, am I on track?",
                "Should I increase my risk tolerance or play it safe?"
            ]
        },
        {
            "profile": "Conservative Investor (Age 60)",
            "queries": [
                "I need income-focused investments for retirement",
                "How can I protect my wealth from inflation?",
                "What's the safest way to generate 4% annual income?",
                "I prefer Sharia-compliant investments only"
            ]
        },
        {
            "profile": "High Net Worth Individual",
            "queries": [
                "I have $1M to diversify across global markets",
                "How can I minimize risk while maintaining growth?",
                "What alternative investments should I consider?",
                "I need estate planning and wealth preservation strategies"
            ]
        }
    ]
    
    for example in examples:
        print(f"\n--- {example['profile']} ---")
        for i, query in enumerate(example['queries'], 1):
            print(f"{i}. \"{query}\"")

def main():
    """Run comprehensive demo of enhanced financial planner"""
    print("🏦 ENHANCED FINANCIAL PLANNER AI AGENT")
    print("🤖 Comprehensive Demonstration")
    print("="*60)
    
    try:
        # Run all demos
        demo_database()
        demo_portfolio_optimization()
        demo_financial_planning()
        demo_risk_assessment()
        demo_query_examples()
        
        print("\n" + "="*60)
        print("✅ DEMO COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nYour enhanced financial planner now includes:")
        print("• 📊 Comprehensive investment database (UAE + US markets)")
        print("• 🎯 Modern Portfolio Theory optimization")
        print("• 💰 Advanced financial planning calculators")
        print("• 🎯 Sophisticated risk assessment")
        print("• 🤖 AI-powered personalized recommendations")
        print("• 📈 Monte Carlo simulations")
        print("• 🕌 Sharia-compliant investment options")
        print("\nTo use the enhanced planner, run: python main.py")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install -r requirements.txt")

if __name__ == "__main__":
    main()
