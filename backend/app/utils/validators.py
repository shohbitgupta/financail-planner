"""
Input validation utilities.
"""
from typing import Dict, Any, List

def validate_user_input(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate user input data for financial planning."""
    
    errors = []
    
    # Required fields
    required_fields = ['age', 'retirement_age', 'annual_salary', 'annual_expenses', 'current_savings', 'risk_tolerance']
    
    for field in required_fields:
        if field not in user_data:
            errors.append(f"Missing required field: {field}")
    
    if errors:
        return {'valid': False, 'errors': errors}
    
    # Age validation
    age = user_data.get('age')
    retirement_age = user_data.get('retirement_age')
    
    try:
        age = int(age)
        retirement_age = int(retirement_age)
        
        if age < 18 or age > 100:
            errors.append("Age must be between 18 and 100")
        
        if retirement_age <= age:
            errors.append("Retirement age must be greater than current age")
        
        if retirement_age > 100:
            errors.append("Retirement age must be 100 or less")
            
    except (ValueError, TypeError):
        errors.append("Age and retirement age must be valid numbers")
    
    # Financial validation
    financial_fields = ['annual_salary', 'annual_expenses', 'current_savings']
    
    for field in financial_fields:
        try:
            value = float(user_data.get(field, 0))
            if value < 0:
                errors.append(f"{field.replace('_', ' ').title()} cannot be negative")
        except (ValueError, TypeError):
            errors.append(f"{field.replace('_', ' ').title()} must be a valid number")
    
    # Risk tolerance validation
    risk_tolerance = user_data.get('risk_tolerance', '').lower()
    valid_risk_levels = ['conservative', 'moderate', 'aggressive']
    
    if risk_tolerance not in valid_risk_levels:
        errors.append(f"Risk tolerance must be one of: {', '.join(valid_risk_levels)}")
    
    # Market validation (optional)
    if 'preferred_market' in user_data:
        preferred_market = user_data.get('preferred_market')
        valid_markets = ['UAE', 'US', 'Global']
        if preferred_market not in valid_markets:
            errors.append(f"Preferred market must be one of: {', '.join(valid_markets)}")
    
    # Goals validation (optional)
    if 'goals' in user_data:
        goals = user_data.get('goals')
        if not isinstance(goals, list) or len(goals) == 0:
            errors.append("Goals must be a non-empty list")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

def validate_portfolio_allocation(allocations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate portfolio allocation data."""
    
    errors = []
    
    if not allocations:
        errors.append("Portfolio allocations cannot be empty")
        return {'valid': False, 'errors': errors}
    
    total_allocation = 0
    
    for i, allocation in enumerate(allocations):
        # Check required fields
        required_fields = ['symbol', 'allocation_percentage', 'investment_amount']
        
        for field in required_fields:
            if field not in allocation:
                errors.append(f"Allocation {i+1}: Missing required field '{field}'")
        
        # Validate allocation percentage
        try:
            percentage = float(allocation.get('allocation_percentage', 0))
            if percentage < 0 or percentage > 100:
                errors.append(f"Allocation {i+1}: Percentage must be between 0 and 100")
            total_allocation += percentage
        except (ValueError, TypeError):
            errors.append(f"Allocation {i+1}: Allocation percentage must be a valid number")
        
        # Validate investment amount
        try:
            amount = float(allocation.get('investment_amount', 0))
            if amount < 0:
                errors.append(f"Allocation {i+1}: Investment amount cannot be negative")
        except (ValueError, TypeError):
            errors.append(f"Allocation {i+1}: Investment amount must be a valid number")
    
    # Check total allocation
    if abs(total_allocation - 100) > 1:  # Allow 1% tolerance
        errors.append(f"Total allocation is {total_allocation:.1f}%, should be close to 100%")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

def validate_financial_metrics(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Validate financial metrics data."""
    
    errors = []
    
    # Check for required metrics
    required_metrics = ['expected_return', 'risk_level', 'volatility']
    
    for metric in required_metrics:
        if metric not in metrics:
            errors.append(f"Missing required metric: {metric}")
    
    # Validate expected return
    if 'expected_return' in metrics:
        try:
            expected_return = float(metrics['expected_return'])
            if expected_return < -1 or expected_return > 1:  # -100% to 100%
                errors.append("Expected return must be between -100% and 100%")
        except (ValueError, TypeError):
            errors.append("Expected return must be a valid number")
    
    # Validate risk level
    if 'risk_level' in metrics:
        try:
            risk_level = int(metrics['risk_level'])
            if risk_level < 1 or risk_level > 10:
                errors.append("Risk level must be between 1 and 10")
        except (ValueError, TypeError):
            errors.append("Risk level must be a valid integer")
    
    # Validate volatility
    if 'volatility' in metrics:
        try:
            volatility = float(metrics['volatility'])
            if volatility < 0 or volatility > 1:  # 0% to 100%
                errors.append("Volatility must be between 0% and 100%")
        except (ValueError, TypeError):
            errors.append("Volatility must be a valid number")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }
