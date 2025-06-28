"""
Helper utility functions.
"""
import json
import math
from typing import Any, Dict, List, Union

def clean_nan_values(data: Any) -> Any:
    """Recursively clean NaN values from data structures."""
    
    if isinstance(data, dict):
        cleaned = {}
        for key, value in data.items():
            cleaned[key] = clean_nan_values(value)
        return cleaned
    
    elif isinstance(data, list):
        return [clean_nan_values(item) for item in data]
    
    elif isinstance(data, float):
        if math.isnan(data) or math.isinf(data):
            return 0.0
        return data
    
    else:
        return data

def safe_json_dumps(data: Any) -> str:
    """Safely serialize data to JSON, handling NaN values."""
    cleaned_data = clean_nan_values(data)
    return json.dumps(cleaned_data, default=str)

def format_currency(amount: float, currency: str = 'AED') -> str:
    """Format amount as currency string."""
    if currency == 'AED':
        return f"AED {amount:,.2f}"
    elif currency == 'USD':
        return f"${amount:,.2f}"
    else:
        return f"{currency} {amount:,.2f}"

def format_percentage(value: float, decimal_places: int = 2) -> str:
    """Format value as percentage string."""
    return f"{value:.{decimal_places}f}%"

def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values."""
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / old_value) * 100

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length with suffix."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def validate_email(email: str) -> bool:
    """Basic email validation."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def generate_portfolio_id(user_id: str, timestamp: str = None) -> str:
    """Generate unique portfolio ID."""
    import hashlib
    from datetime import datetime
    
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    
    data = f"{user_id}_{timestamp}"
    return hashlib.md5(data.encode()).hexdigest()[:12]

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def merge_dictionaries(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple dictionaries, with later ones taking precedence."""
    result = {}
    for d in dicts:
        result.update(d)
    return result

def get_nested_value(data: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """Get nested value from dictionary using dot notation."""
    keys = key_path.split('.')
    current = data
    
    try:
        for key in keys:
            current = current[key]
        return current
    except (KeyError, TypeError):
        return default

def set_nested_value(data: Dict[str, Any], key_path: str, value: Any) -> None:
    """Set nested value in dictionary using dot notation."""
    keys = key_path.split('.')
    current = data
    
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value

def flatten_dict(data: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Flatten nested dictionary."""
    items = []
    
    for key, value in data.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, sep=sep).items())
        else:
            items.append((new_key, value))
    
    return dict(items)

def unflatten_dict(data: Dict[str, Any], sep: str = '.') -> Dict[str, Any]:
    """Unflatten dictionary with dot notation keys."""
    result = {}
    
    for key, value in data.items():
        set_nested_value(result, key, value)
    
    return result
