#!/usr/bin/env python3
"""
Test script to verify WIO platform recommendations are working correctly
"""

import requests
import json
import sys

def test_platform_recommendations():
    """Test the API to ensure platform recommendations are included"""
    
    # Test data
    test_data = {
        "age": 30,
        "retirement_age": 60,
        "annual_salary": 120000,
        "annual_expenses": 80000,
        "current_savings": 50000,
        "monthly_investment": 2000,
        "risk_tolerance": "moderate",
        "goals": ["retirement"],
        "is_sharia_compliant": False,
        "preferred_market": "UAE",
        "currency": "AED"
    }
    
    print("🧪 Testing WIO Platform Recommendations...")
    print("=" * 50)
    
    try:
        # Make API request
        response = requests.post(
            "http://localhost:5001/api/generate-financial-plan",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=120
        )
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            return False
            
        data = response.json()
        recommendations = data.get('recommendations', [])
        
        print(f"✅ API Response received successfully")
        print(f"📊 Number of recommendations: {len(recommendations)}")
        print()
        
        platform_found = False
        
        for i, rec in enumerate(recommendations):
            print(f"📈 Recommendation {i+1}:")
            print(f"   Symbol: {rec.get('symbol', 'N/A')}")
            print(f"   Name: {rec.get('name', 'N/A')}")
            print(f"   Category: {rec.get('category', 'N/A')}")
            
            if 'platform_recommendation' in rec and rec['platform_recommendation']:
                platform = rec['platform_recommendation']
                platform_found = True
                print(f"   ✅ Platform: {platform.get('platform_name', 'N/A')}")
                print(f"   ✅ App: {platform.get('app_name', 'N/A')}")
                print(f"   ✅ Type: {platform.get('platform_type', 'N/A')}")
                
                # Check for expected WIO platforms
                app_name = platform.get('app_name', '')
                if 'WIO Invest' in app_name:
                    print(f"   🎯 Found WIO Invest App for {rec.get('category')} investment!")
                elif 'WIO Personal' in app_name:
                    print(f"   🎯 Found WIO Personal Saving Spaces for {rec.get('category')} investment!")
                elif 'WIO Banking' in app_name:
                    print(f"   🎯 Found WIO Banking App for {rec.get('category')} investment!")
            else:
                print(f"   ❌ No platform recommendation found")
            print()
        
        if platform_found:
            print("🎉 SUCCESS: WIO Platform recommendations are working correctly!")
            return True
        else:
            print("❌ FAILURE: No platform recommendations found in any recommendation")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network Error: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON Parse Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    success = test_platform_recommendations()
    sys.exit(0 if success else 1)
