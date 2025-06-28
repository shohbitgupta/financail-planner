"""
API blueprints for Financial Planner AI.
"""
from .financial_planning import financial_planning_bp
from .health import health_bp

__all__ = ['financial_planning_bp', 'health_bp']
