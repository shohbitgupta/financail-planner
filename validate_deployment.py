#!/usr/bin/env python3
"""
Deployment Validation Script for Financial Planner AI Agent
Tests all components to ensure successful deployment
"""

import requests
import json
import os
import sys
from pathlib import Path
import subprocess

def test_api_health(base_url):
    """Test API health endpoint"""
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code == 200:
            print("✅ API Health Check: PASSED")
            return True
        else:
            print(f"❌ API Health Check: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ API Health Check: FAILED (Error: {e})")
        return False

def test_financial_plan_generation(base_url):
    """Test financial plan generation endpoint"""
    test_data = {
        "goal": "retirement",
        "age": 30,
        "retirement_age": 60,
        "annual_salary": 200000,
        "annual_expenses": 120000,
        "market_type": "UAE",
        "current_savings": 50000,
        "risk_appetite": "moderate"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/generate-financial-plan",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'recommendations' in data and len(data['recommendations']) > 0:
                print("✅ Financial Plan Generation: PASSED")
                return True
            else:
                print("❌ Financial Plan Generation: FAILED (No recommendations)")
                return False
        else:
            print(f"❌ Financial Plan Generation: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Financial Plan Generation: FAILED (Error: {e})")
        return False

def test_frontend_build():
    """Test if React frontend is built"""
    build_path = Path("react_financial_ui/build")
    if build_path.exists() and (build_path / "index.html").exists():
        print("✅ React Build: PASSED")
        return True
    else:
        print("❌ React Build: FAILED (Build directory not found)")
        return False

def test_environment_variables():
    """Test if required environment variables are set"""
    required_vars = ['GEMINI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if not missing_vars:
        print("✅ Environment Variables: PASSED")
        return True
    else:
        print(f"❌ Environment Variables: FAILED (Missing: {', '.join(missing_vars)})")
        return False

def test_database_files():
    """Test if database files exist"""
    db_files = [
        "flask_api/investment_database.db",
        "enhanced_investment_vector_db"
    ]
    
    missing_files = []
    for file_path in db_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if not missing_files:
        print("✅ Database Files: PASSED")
        return True
    else:
        print(f"❌ Database Files: FAILED (Missing: {', '.join(missing_files)})")
        return False

def test_python_imports():
    """Test if Python modules can be imported"""
    try:
        sys.path.insert(0, str(Path.cwd()))
        from flask_api.standalone_app import app
        from flask_api.evaluator_agent import FinancialPlanEvaluator
        print("✅ Python Imports: PASSED")
        return True
    except ImportError as e:
        print(f"❌ Python Imports: FAILED (Error: {e})")
        return False

def main():
    """Main validation function"""
    print("🔍 Financial Planner AI Agent - Deployment Validation")
    print("=" * 55)
    
    # Get base URL from command line or use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5001"
    print(f"Testing deployment at: {base_url}")
    print()
    
    # Run all tests
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Database Files", test_database_files),
        ("Python Imports", test_python_imports),
        ("React Build", test_frontend_build),
        ("API Health", lambda: test_api_health(base_url)),
        ("Financial Plan Generation", lambda: test_financial_plan_generation(base_url))
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"Running {test_name} test...")
        result = test_func()
        results.append((test_name, result))
        print()
    
    # Summary
    print("📊 Validation Summary")
    print("-" * 25)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print()
    print(f"Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Deployment is successful!")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    exit(main())
