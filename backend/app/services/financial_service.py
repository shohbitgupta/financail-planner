"""
Main financial planning service that orchestrates all components.
"""
import logging
from typing import Dict, Any, List
from backend.app.models.user_profile import UserProfile
from backend.app.services import llm_service, evaluator_service, vector_service, portfolio_service
from backend.app.utils.calculations import FinancialCalculator

logger = logging.getLogger(__name__)

def generate_comprehensive_plan(user_profile: UserProfile) -> Dict[str, Any]:
    """Generate a comprehensive financial plan for the user."""
    
    try:
        logger.info(f"Generating comprehensive plan for user: age={user_profile.age}")
        
        # 1. Get contextual investment recommendations from vector database
        investment_context = vector_service.get_contextual_recommendations(user_profile)
        
        # 2. Generate initial response using LLM
        llm_response = llm_service.generate_financial_plan(user_profile, investment_context)
        
        # 3. Evaluate and improve response using Gemini
        evaluation_result = evaluator_service.evaluate_and_improve(llm_response, user_profile)
        final_response = evaluation_result["improved_response"]
        evaluation_metadata = evaluation_result["evaluation_metadata"]
        
        # 4. Generate portfolio recommendations
        portfolio_recommendations = portfolio_service.generate_recommendations(user_profile)
        
        # 5. Calculate financial metrics
        financial_metrics = _calculate_financial_metrics(user_profile)
        
        # 6. Build comprehensive response
        comprehensive_plan = {
            # Core LLM response
            "raw_llm_response": final_response,
            "executive_summary": _extract_executive_summary(final_response),
            
            # Portfolio recommendations
            "recommendations": [rec.to_dict() for rec in portfolio_recommendations],
            "total_allocation": _calculate_total_allocation(portfolio_recommendations),
            
            # Financial analysis
            "financial_metrics": financial_metrics,
            "monthly_savings_needed": financial_metrics.get("additional_monthly_needed", 0),
            "expected_portfolio_return": _calculate_portfolio_return(portfolio_recommendations),
            
            # Analysis sections
            "risk_assessment": _generate_risk_assessment(user_profile, portfolio_recommendations),
            "time_horizon_analysis": _generate_time_horizon_analysis(user_profile),
            "goal_achievement_timeline": _generate_goal_timeline(user_profile),
            
            # Additional information
            "compliance_notes": _generate_compliance_notes(user_profile),
            "additional_advice": _generate_additional_advice(user_profile),
            
            # Metadata
            "user_profile": user_profile.to_dict(),
            "evaluation_metadata": evaluation_metadata
        }
        
        logger.info("Comprehensive financial plan generated successfully")
        return comprehensive_plan
        
    except Exception as e:
        logger.error(f"Error generating comprehensive plan: {str(e)}")
        raise

def get_portfolio_recommendations(user_profile: UserProfile) -> List[Dict[str, Any]]:
    """Get portfolio recommendations for the user."""
    try:
        recommendations = portfolio_service.generate_recommendations(user_profile)
        return [rec.to_dict() for rec in recommendations]
    except Exception as e:
        logger.error(f"Error getting portfolio recommendations: {str(e)}")
        raise

def assess_risk_profile(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Assess user risk profile."""
    try:
        user_profile = UserProfile.from_dict(user_data)
        
        risk_assessment = {
            "risk_score": user_profile.get_risk_score(),
            "risk_category": _get_risk_category(user_profile.get_risk_score()),
            "risk_factors": _analyze_risk_factors(user_profile),
            "recommendations": _get_risk_recommendations(user_profile)
        }
        
        return risk_assessment
    except Exception as e:
        logger.error(f"Error assessing risk profile: {str(e)}")
        raise

def _calculate_financial_metrics(user_profile: UserProfile) -> Dict[str, Any]:
    """Calculate comprehensive financial metrics."""
    calculator = FinancialCalculator()
    
    # Basic calculations
    monthly_savings_capacity = user_profile.get_monthly_savings_capacity()
    savings_rate = user_profile.get_savings_rate()
    investment_horizon = user_profile.investment_horizon
    
    # Retirement corpus calculation (80% income replacement)
    target_annual_income = user_profile.annual_salary * 0.8
    retirement_corpus_needed = target_annual_income / 0.04  # 4% withdrawal rule
    
    # Future value calculation
    annual_return = 0.07  # Assumed 7% return
    total_accumulated = calculator.calculate_future_value(
        present_value=user_profile.current_savings,
        monthly_payment=monthly_savings_capacity,
        annual_rate=annual_return,
        years=investment_horizon
    )
    
    # Check if on track
    shortfall = max(0, retirement_corpus_needed - total_accumulated)
    additional_monthly_needed = 0
    if shortfall > 0:
        additional_monthly_needed = calculator.calculate_monthly_payment_needed(
            future_value=shortfall,
            annual_rate=annual_return,
            years=investment_horizon
        )
    
    return {
        "monthly_savings_capacity": monthly_savings_capacity,
        "savings_rate": savings_rate,
        "investment_horizon": investment_horizon,
        "retirement_corpus_needed": retirement_corpus_needed,
        "total_accumulated": total_accumulated,
        "shortfall": shortfall,
        "additional_monthly_needed": additional_monthly_needed,
        "is_on_track": shortfall == 0
    }

def _calculate_total_allocation(recommendations) -> Dict[str, float]:
    """Calculate total allocation by category."""
    allocation = {}
    for rec in recommendations:
        category = rec.category
        if category in allocation:
            allocation[category] += rec.allocation_percentage
        else:
            allocation[category] = rec.allocation_percentage
    return allocation

def _calculate_portfolio_return(recommendations) -> float:
    """Calculate weighted portfolio expected return."""
    if not recommendations:
        return 0.0
    
    total_weight = sum(rec.allocation_percentage for rec in recommendations)
    if total_weight == 0:
        return 0.0
    
    weighted_return = sum(
        rec.expected_return * (rec.allocation_percentage / total_weight)
        for rec in recommendations
    )
    return weighted_return

def _extract_executive_summary(llm_response: str) -> str:
    """Extract executive summary from LLM response."""
    lines = llm_response.split('\n')
    summary_lines = []
    in_summary = False
    
    for line in lines:
        if 'EXECUTIVE SUMMARY' in line.upper():
            in_summary = True
            continue
        elif line.startswith('**') and in_summary:
            break
        elif in_summary and line.strip():
            summary_lines.append(line.strip())
    
    if summary_lines:
        return ' '.join(summary_lines)
    else:
        return "Based on your profile, you need additional monthly savings to meet your retirement goals"

def _generate_risk_assessment(user_profile: UserProfile, recommendations) -> str:
    """Generate risk assessment text."""
    risk_score = user_profile.get_risk_score()
    risk_category = _get_risk_category(risk_score)

    # Include recommendation count in assessment
    rec_count = len(recommendations) if recommendations else 0
    return f"Your {user_profile.risk_tolerance} risk profile ({risk_category}) is suitable for your {user_profile.investment_horizon}-year investment horizon. Portfolio includes {rec_count} recommended instruments."

def _generate_time_horizon_analysis(user_profile: UserProfile) -> str:
    """Generate time horizon analysis."""
    years = user_profile.investment_horizon
    if years >= 20:
        return f"With {years} years until retirement, you have time for growth-oriented investments"
    elif years >= 10:
        return f"With {years} years until retirement, a balanced approach is recommended"
    else:
        return f"With {years} years until retirement, focus on capital preservation"

def _generate_goal_timeline(user_profile: UserProfile) -> Dict[str, int]:
    """Generate goal achievement timeline."""
    timeline = {}
    for goal in user_profile.goals:
        if goal.lower() == 'retirement':
            timeline[goal] = user_profile.investment_horizon
        else:
            timeline[goal] = min(10, user_profile.investment_horizon)  # Default to 10 years or less
    return timeline

def _generate_compliance_notes(user_profile: UserProfile) -> str:
    """Generate compliance notes."""
    notes = []
    if user_profile.is_sharia_compliant:
        notes.append("Sharia-compliant investments recommended")
    if user_profile.preferred_market == 'UAE':
        notes.append("UAE market focus with regulatory compliance")
    return "; ".join(notes) if notes else "Standard investment compliance applies"

def _generate_additional_advice(user_profile: UserProfile) -> List[str]:
    """Generate additional advice."""
    advice = [
        "Start investing early to benefit from compound growth",
        "Diversify your portfolio across different asset classes",
        "Review and rebalance your portfolio annually",
        "Consider tax-efficient investment vehicles"
    ]
    
    if user_profile.is_sharia_compliant:
        advice.append("Ensure all investments maintain Sharia compliance")
    
    if user_profile.get_savings_rate() < 0.2:
        advice.append("Consider increasing your savings rate for better retirement outcomes")
    
    return advice

def _get_risk_category(risk_score: int) -> str:
    """Get risk category from score."""
    if risk_score <= 3:
        return "Conservative"
    elif risk_score <= 6:
        return "Moderate"
    elif risk_score <= 8:
        return "Aggressive"
    else:
        return "Very Aggressive"

def _analyze_risk_factors(user_profile: UserProfile) -> List[str]:
    """Analyze risk factors for the user."""
    factors = []
    
    if user_profile.age < 30:
        factors.append("Young age allows for higher risk tolerance")
    elif user_profile.age > 50:
        factors.append("Approaching retirement suggests lower risk tolerance")
    
    if user_profile.investment_horizon > 20:
        factors.append("Long investment horizon supports growth investments")
    elif user_profile.investment_horizon < 10:
        factors.append("Short investment horizon suggests conservative approach")
    
    if user_profile.get_savings_rate() > 0.3:
        factors.append("High savings rate provides flexibility for risk-taking")
    
    return factors

def _get_risk_recommendations(user_profile: UserProfile) -> List[str]:
    """Get risk-based recommendations."""
    recommendations = []
    
    risk_score = user_profile.get_risk_score()
    
    if risk_score <= 3:
        recommendations.extend([
            "Focus on bonds and fixed-income investments",
            "Consider capital preservation strategies",
            "Limit equity exposure to 30% or less"
        ])
    elif risk_score <= 6:
        recommendations.extend([
            "Balance between growth and stability",
            "Consider 50-70% equity allocation",
            "Include defensive assets for stability"
        ])
    else:
        recommendations.extend([
            "Focus on growth investments",
            "Consider 70-90% equity allocation",
            "Include emerging markets for higher returns"
        ])
    
    return recommendations
