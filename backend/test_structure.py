#!/usr/bin/env python3
"""
Test script to verify the backend structure works correctly.
"""
import sys
import os
from pathlib import Path

# Add backend to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def test_imports():
    """Test that all modules can be imported."""
    
    print("Testing imports...")
    
    try:
        # Test config import
        from config import config
        print("✓ Config imported successfully")
        
        # Test models
        from app.models.user_profile import UserProfile
        from app.models.portfolio import PortfolioRecommendation
        from app.models.investment import Investment
        print("✓ Models imported successfully")
        
        # Test utils
        from app.utils.calculations import FinancialCalculator
        from app.utils.validators import validate_user_input
        from app.utils.helpers import clean_nan_values
        print("✓ Utils imported successfully")
        
        # Test services (without initialization)
        from app.services import financial_service, portfolio_service
        print("✓ Services imported successfully")
        
        # Test database modules
        from app.database.investment_db import InvestmentDatabase
        from app.database.vector_db import VectorDatabase
        print("✓ Database modules imported successfully")
        
        # Test API modules
        from app.api.financial_planning import financial_planning_bp
        from app.api.health import health_bp
        print("✓ API modules imported successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {str(e)}")
        return False

def test_models():
    """Test model creation and validation."""

    print("\nTesting models...")

    try:
        # Re-import models
        from app.models.user_profile import UserProfile
        from app.models.investment import Investment

        # Test UserProfile
        user_profile = UserProfile(
            age=30,
            retirement_age=65,
            annual_salary=100000,
            annual_expenses=60000,
            current_savings=50000,
            risk_tolerance='moderate',
            goals=['retirement', 'house'],
            preferred_market='UAE',
            is_sharia_compliant=False
        )
        
        assert user_profile.investment_horizon == 35
        assert user_profile.get_monthly_savings_capacity() > 0
        print("✓ UserProfile model works correctly")
        
        # Test Investment
        investment = Investment(
            symbol='TEST_STOCK',
            name='Test Stock',
            category='Equity',
            market='UAE',
            currency='AED',
            expected_return=0.08,
            risk_level=5
        )
        
        assert investment.symbol == 'TEST_STOCK'
        print("✓ Investment model works correctly")
        
        return True
        
    except Exception as e:
        print(f"✗ Model test failed: {str(e)}")
        return False

def test_utils():
    """Test utility functions."""

    print("\nTesting utilities...")

    try:
        # Re-import utils
        from app.utils.calculations import FinancialCalculator

        # Test FinancialCalculator
        calc = FinancialCalculator()
        
        future_value = calc.calculate_future_value(10000, 1000, 0.08, 10)
        assert future_value > 10000
        print("✓ FinancialCalculator works correctly")
        
        # Test validators
        from app.utils.validators import validate_user_input
        
        valid_data = {
            'age': 30,
            'retirement_age': 65,
            'annual_salary': 100000,
            'annual_expenses': 60000,
            'current_savings': 50000,
            'risk_tolerance': 'moderate'
        }
        
        result = validate_user_input(valid_data)
        assert result['valid'] == True
        print("✓ Input validation works correctly")
        
        # Test helpers
        from app.utils.helpers import clean_nan_values
        import math
        
        dirty_data = {'value': math.nan, 'clean': 42}
        clean_data = clean_nan_values(dirty_data)
        assert clean_data['value'] == 0.0
        assert clean_data['clean'] == 42
        print("✓ Helper functions work correctly")
        
        return True
        
    except Exception as e:
        print(f"✗ Utils test failed: {str(e)}")
        return False

def test_flask_app():
    """Test Flask app creation."""
    
    print("\nTesting Flask app creation...")
    
    try:
        # Set required environment variables
        os.environ.setdefault('GEMINI_API_KEY', 'test_key')
        
        from app import create_app
        
        # Create app in testing mode
        app = create_app('testing')
        
        assert app is not None
        assert app.config['TESTING'] == True
        print("✓ Flask app created successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Flask app test failed: {str(e)}")
        return False

def main():
    """Run all tests."""
    
    print("=" * 50)
    print("Backend Structure Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_models,
        test_utils,
        test_flask_app
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend structure is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
