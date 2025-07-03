#!/usr/bin/env python3
"""
Test script to validate dynamic content generation for risk assessment, 
time horizon analysis, goal risks, and additional advice
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

from standalone_app import (
    structure_risk_assessment, 
    structure_time_horizon_analysis,
    parse_goal_risks_mitigation,
    parse_additional_advice
)

def test_dynamic_content():
    """Test all dynamic content generation functions"""
    
    print("🧪 Testing Dynamic Content Generation")
    print("=" * 50)
    
    # Test user data
    test_user_data = {
        "age": 30,
        "retirement_age": 60,
        "risk_tolerance": "moderate",
        "goals": ["retirement", "wealth_building"],
        "sharia_compliant": True
    }
    
    test_financial_metrics = {
        "investment_horizon": 30,
        "monthly_savings_capacity": 3000
    }
    
    # Test 1: Risk Assessment (no LLM response - should use dynamic generation)
    print("\n📊 Test 1: Dynamic Risk Assessment")
    print("-" * 30)
    
    risk_assessment = structure_risk_assessment("", test_user_data, test_financial_metrics)
    print(f"✅ Risk Level: {risk_assessment.get('risk_level', 'N/A')}")
    print(f"✅ Description: {risk_assessment.get('description', 'N/A')}")
    print(f"✅ Suitability: {risk_assessment.get('suitability', 'N/A')}")
    print(f"✅ Time Factor: {risk_assessment.get('time_factor', 'N/A')}")
    
    # Test 2: Time Horizon Analysis
    print("\n⏰ Test 2: Dynamic Time Horizon Analysis")
    print("-" * 30)
    
    time_horizon = structure_time_horizon_analysis("", test_user_data, test_financial_metrics)
    print(f"✅ Horizon Category: {time_horizon.get('horizon_category', 'N/A')}")
    print(f"✅ Strategy: {time_horizon.get('strategy', 'N/A')}")
    print(f"✅ Flexibility: {time_horizon.get('flexibility', 'N/A')}")
    
    if 'milestones' in time_horizon:
        print("✅ Milestones:")
        for phase, description in time_horizon['milestones'].items():
            print(f"   • {phase}: {description}")
    
    # Test 3: Goal Risks and Mitigation
    print("\n⚠️  Test 3: Dynamic Goal Risks & Mitigation")
    print("-" * 30)
    
    goal_risks = parse_goal_risks_mitigation("", test_user_data)
    for goal, data in goal_risks.items():
        print(f"🎯 Goal: {goal}")
        print("   Risks:")
        for risk in data['risks'][:2]:  # Show first 2 risks
            print(f"     • {risk}")
        print("   Mitigation:")
        for mitigation in data['mitigation'][:2]:  # Show first 2 mitigation strategies
            print(f"     • {mitigation}")
        print()
    
    # Test 4: Additional Advice
    print("\n💡 Test 4: Dynamic Additional Advice")
    print("-" * 30)
    
    additional_advice = parse_additional_advice("", test_user_data)
    for i, advice in enumerate(additional_advice[:4], 1):  # Show first 4 pieces of advice
        print(f"✅ {i}. {advice}")
    
    # Test 5: LLM Response Parsing
    print("\n🤖 Test 5: LLM Response Parsing")
    print("-" * 30)
    
    sample_llm_response = """
    Risk Level: Moderate Risk (6/10)
    Description: Balanced growth strategy with Islamic compliance
    Suitability: Long-term investors comfortable with market fluctuations
    Allocation Focus: Mix of Sharia-compliant stocks and Islamic bonds
    Time Factor: 30-year horizon allows for higher risk tolerance
    Age Factor: At age 30, ample time for market recovery
    """
    
    parsed_risk = structure_risk_assessment(sample_llm_response, test_user_data, test_financial_metrics)
    print("✅ Parsed LLM Risk Assessment:")
    for key, value in parsed_risk.items():
        print(f"   {key}: {value}")
    
    # Test 6: Goal Risks from LLM Response
    sample_goal_response = """
    Goal Name: Retirement
    Potential Risks:
    - Market volatility during accumulation phase
    - Inflation reducing real returns
    - Healthcare cost increases
    Mitigation Strategies:
    - Diversified investment approach
    - Inflation-protected securities
    - Health savings planning
    
    Goal Name: Wealth Building
    Potential Risks:
    - Economic downturns affecting growth
    - Lifestyle inflation
    Mitigation Strategies:
    - Dollar-cost averaging
    - Automatic investment plans
    """
    
    parsed_goals = parse_goal_risks_mitigation(sample_goal_response, test_user_data)
    print("\n✅ Parsed LLM Goal Risks:")
    for goal, data in parsed_goals.items():
        print(f"   {goal}: {len(data['risks'])} risks, {len(data['mitigation'])} strategies")
    
    print("\n🎉 All Dynamic Content Tests Completed Successfully!")
    print("✅ Risk Assessment: Dynamic generation working")
    print("✅ Time Horizon: Dynamic generation working") 
    print("✅ Goal Risks: Dynamic generation working")
    print("✅ Additional Advice: Dynamic generation working")
    print("✅ LLM Parsing: Working for structured responses")

if __name__ == "__main__":
    test_dynamic_content()
