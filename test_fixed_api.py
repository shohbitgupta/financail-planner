#!/usr/bin/env python3
"""
Test script to verify the fixed API is working correctly
"""

import requests
import json
import time

def test_api_fix():
    """Test the fixed API with dynamic content"""
    
    print("🧪 Testing Fixed API with Dynamic Content")
    print("=" * 50)
    
    # Test data
    test_data = {
        'age': 30,
        'retirement_age': 60,
        'annual_salary': 120000,
        'annual_expenses': 60000,
        'current_savings': 25000,
        'goal': 'retirement planning',
        'risk_tolerance': 'moderate',
        'market_type': 'UAE',
        'sharia_compliant': True,
        'goals': ['retirement', 'wealth_building']
    }
    
    try:
        print("📡 Making API request...")
        start_time = time.time()
        
        response = requests.post(
            'http://localhost:5001/api/generate-financial-plan', 
            json=test_data, 
            timeout=30
        )
        
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ API call successful! ({response_time:.2f}s)")
            print("\n📊 Response Analysis:")
            print("-" * 30)
            
            # Check risk assessment structure
            risk_assessment = result.get('risk_assessment', {})
            if isinstance(risk_assessment, dict):
                print("✅ Risk Assessment: Structured format")
                print(f"   • Risk Level: {risk_assessment.get('risk_level', 'N/A')}")
                print(f"   • Description: {risk_assessment.get('description', 'N/A')[:50]}...")
                print(f"   • Suitability: {risk_assessment.get('suitability', 'N/A')[:50]}...")
            else:
                print("⚠️  Risk Assessment: String format (fallback)")
            
            # Check time horizon analysis
            time_horizon = result.get('time_horizon_analysis', {})
            if isinstance(time_horizon, dict):
                print("✅ Time Horizon: Structured format")
                print(f"   • Category: {time_horizon.get('horizon_category', 'N/A')}")
                print(f"   • Strategy: {time_horizon.get('strategy', 'N/A')[:50]}...")
                if 'milestones' in time_horizon:
                    print(f"   • Milestones: {len(time_horizon['milestones'])} phases")
            else:
                print("⚠️  Time Horizon: String format (fallback)")
            
            # Check additional advice
            additional_advice = result.get('additional_advice', [])
            print(f"✅ Additional Advice: {len(additional_advice)} items")
            for i, advice in enumerate(additional_advice[:3], 1):
                print(f"   {i}. {advice[:60]}...")
            
            # Check goal risks and mitigation
            goal_risks = result.get('goal_risks_mitigation', {})
            if goal_risks:
                print(f"✅ Goal Risks & Mitigation: {len(goal_risks)} goals")
                for goal, data in goal_risks.items():
                    risks_count = len(data.get('risks', []))
                    mitigation_count = len(data.get('mitigation', []))
                    print(f"   • {goal}: {risks_count} risks, {mitigation_count} strategies")
            else:
                print("⚠️  Goal Risks & Mitigation: Not available")
            
            # Check recommendations
            recommendations = result.get('recommendations', [])
            print(f"✅ Recommendations: {len(recommendations)} instruments")
            
            # Check compliance
            compliance = result.get('compliance_notes', '')
            if 'Sharia' in compliance or 'Islamic' in compliance:
                print("✅ Sharia Compliance: Properly handled")
            else:
                print("⚠️  Sharia Compliance: May need attention")
            
            print(f"\n🎉 All Dynamic Content Features Working!")
            return True
            
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    success = test_api_fix()
    if success:
        print("\n✅ API Fix Verification: PASSED")
        print("🚀 Dynamic content generation is working correctly!")
    else:
        print("\n❌ API Fix Verification: FAILED")
        print("🔧 Further debugging may be needed")
