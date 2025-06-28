#!/usr/bin/env python3
"""
Test script for the Financial Plan Evaluator Agent
This script demonstrates the evaluator functionality without requiring API keys
"""

import json
import requests
import time

def test_financial_plan_generation():
    """Test the financial plan generation with evaluator integration"""
    
    print("🧪 Testing Financial Plan Evaluator Agent")
    print("=" * 50)
    
    # Test user profile
    test_user_data = {
        "age": 30,
        "retirement_age": 60,
        "annual_salary": 100000,
        "annual_expenses": 60000,
        "current_savings": 50000,
        "risk_tolerance": "aggressive",
        "goals": ["retirement", "house"],
        "is_sharia_compliant": False,
        "preferred_market": "US",
        "currency": "USD"
    }
    
    print("📋 Test User Profile:")
    for key, value in test_user_data.items():
        print(f"   {key}: {value}")
    
    print("\n🚀 Generating financial plan...")
    
    # Make API call
    try:
        start_time = time.time()
        
        response = requests.post(
            'http://localhost:5001/api/generate-financial-plan',
            json=test_user_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Request successful! (Processing time: {processing_time:.1f}s)")
            print("\n📊 Evaluation Metadata:")
            
            # Check evaluation metadata
            eval_metadata = data.get('evaluation_metadata', {})
            if eval_metadata:
                print(f"   Evaluator Used: {eval_metadata.get('evaluator_used', False)}")
                if eval_metadata.get('evaluator_used'):
                    print(f"   Original Score: {eval_metadata.get('original_score', 'N/A')}")
                    print(f"   Improvement Applied: {eval_metadata.get('improvement_applied', False)}")
                    print(f"   Timestamp: {eval_metadata.get('evaluation_timestamp', 'N/A')}")
                else:
                    print(f"   Reason: {eval_metadata.get('reason', 'Unknown')}")
                    if 'error' in eval_metadata:
                        print(f"   Error: {eval_metadata['error']}")
            else:
                print("   No evaluation metadata found")
            
            print("\n💼 Portfolio Recommendations:")
            recommendations = data.get('recommendations', [])
            if recommendations:
                for i, rec in enumerate(recommendations[:5], 1):  # Show first 5
                    print(f"   {i}. {rec.get('name', 'Unknown')} ({rec.get('symbol', 'N/A')})")
                    print(f"      Category: {rec.get('category', 'N/A')}")
                    print(f"      Allocation: {rec.get('allocation_percentage', 0):.1f}%")
                    print(f"      Expected Return: {rec.get('expected_return', 0)*100:.1f}%")
                    print()
            else:
                print("   No recommendations found")
            
            print("📈 Financial Metrics:")
            user_profile = data.get('user_profile', {})
            print(f"   Monthly Investment: ${user_profile.get('monthly_investment', 0):,.0f}")
            print(f"   Investment Horizon: {user_profile.get('investment_horizon', 0)} years")
            print(f"   Risk Tolerance: {user_profile.get('risk_tolerance', 'N/A')}")
            
            # Check if we have raw LLM response for debugging
            if 'raw_llm_response' in data:
                print(f"\n📝 LLM Response Length: {len(data['raw_llm_response'])} characters")
                print("   (Raw response available for debugging)")
            
            return True
            
        else:
            print(f"❌ Request failed with status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out (>30s). This might indicate evaluator processing.")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error. Is the Flask API running on port 5001?")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_api_health():
    """Test API health endpoint"""
    try:
        response = requests.get('http://localhost:5001/api/health', timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print("🏥 API Health Check:")
            print(f"   Status: {health_data.get('status', 'Unknown')}")
            print(f"   Ollama Available: {health_data.get('ollama_available', False)}")
            print(f"   Database Available: {health_data.get('database_available', False)}")
            print(f"   Model: {health_data.get('model', 'Unknown')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def main():
    """Main test function"""
    print("🔬 Financial Plan Evaluator Agent Test Suite")
    print("=" * 60)
    
    # Test 1: API Health
    print("\n1️⃣  Testing API Health...")
    if not test_api_health():
        print("❌ API health check failed. Please ensure Flask API is running.")
        return
    
    print("\n" + "="*60)
    
    # Test 2: Financial Plan Generation
    print("\n2️⃣  Testing Financial Plan Generation with Evaluator...")
    success = test_financial_plan_generation()
    
    print("\n" + "="*60)
    
    # Summary
    if success:
        print("\n🎉 Test completed successfully!")
        print("\n📋 What happened:")
        print("   1. Llama 3.2 generated initial financial plan")
        print("   2. Evaluator agent checked if Gemini API is available")
        print("   3. If available, Gemini 2.5 Pro evaluated the response")
        print("   4. If score < 8.0, Gemini generated improved response")
        print("   5. Final response returned with evaluation metadata")
        
        print("\n🔧 To enable full evaluator functionality:")
        print("   1. Get Gemini API key: https://aistudio.google.com/app/apikey")
        print("   2. Run: python setup_evaluator.py")
        print("   3. Restart Flask API: python standalone_app.py")
    else:
        print("\n❌ Test failed. Please check the Flask API and try again.")

if __name__ == "__main__":
    main()
