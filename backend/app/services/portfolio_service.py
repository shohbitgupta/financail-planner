"""
Portfolio optimization and recommendation service.
"""
import logging
from typing import List, Dict, Any
from app.models.user_profile import UserProfile
from app.models.portfolio import PortfolioRecommendation
from app.models.investment import Investment
from app.database.investment_db import investment_db

logger = logging.getLogger(__name__)

def generate_recommendations(user_profile: UserProfile) -> List[PortfolioRecommendation]:
    """Generate portfolio recommendations based on user profile."""
    
    try:
        logger.info(f"Generating portfolio recommendations for user with {user_profile.risk_tolerance} risk tolerance")
        
        # Get available investments based on user criteria
        investment_criteria = _build_investment_criteria(user_profile)
        available_investments = investment_db.get_investments_by_criteria(investment_criteria)
        
        if not available_investments:
            logger.warning("No investments found matching criteria, using default recommendations")
            return _get_default_recommendations(user_profile)
        
        # Generate optimal allocation
        allocation_strategy = _get_allocation_strategy(user_profile)
        
        # Create recommendations
        recommendations = []
        total_investment = user_profile.get_monthly_savings_capacity() * 12  # Annual investment
        
        for category, target_percentage in allocation_strategy.items():
            category_investments = [inv for inv in available_investments if inv.category == category]
            
            if category_investments:
                # Select best investment in category
                best_investment = _select_best_investment(category_investments, user_profile)
                
                # Calculate allocation
                allocation_percentage = target_percentage
                investment_amount = total_investment * (target_percentage / 100)
                
                # Create recommendation
                rationale = _generate_rationale(best_investment, user_profile, category)
                
                recommendation = PortfolioRecommendation.from_investment(
                    investment=best_investment,
                    allocation_percentage=allocation_percentage,
                    investment_amount=investment_amount,
                    rationale=rationale
                )
                
                recommendations.append(recommendation)
        
        logger.info(f"Generated {len(recommendations)} portfolio recommendations")
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generating portfolio recommendations: {str(e)}")
        return _get_default_recommendations(user_profile)

def _build_investment_criteria(user_profile: UserProfile) -> Dict[str, Any]:
    """Build investment criteria based on user profile."""
    
    criteria = {
        'market': user_profile.preferred_market,
        'max_risk_level': user_profile.get_risk_score(),
        'sharia_compliant': user_profile.is_sharia_compliant
    }
    
    # Add minimum investment constraint if user has limited capital
    monthly_capacity = user_profile.get_monthly_savings_capacity()
    if monthly_capacity < 5000:  # If less than 5000 monthly
        criteria['max_min_investment'] = monthly_capacity * 6  # 6 months worth
    
    return criteria

def _get_allocation_strategy(user_profile: UserProfile) -> Dict[str, float]:
    """Get asset allocation strategy based on user profile."""
    
    risk_score = user_profile.get_risk_score()
    age = user_profile.age
    investment_horizon = user_profile.investment_horizon
    
    # Base allocation on risk tolerance
    if risk_score <= 3:  # Conservative
        allocation = {
            'Bond': 60,
            'Equity': 25,
            'REIT': 10,
            'Commodity': 5
        }
    elif risk_score <= 6:  # Moderate
        allocation = {
            'Equity': 50,
            'Bond': 30,
            'REIT': 15,
            'Commodity': 5
        }
    else:  # Aggressive
        allocation = {
            'Equity': 70,
            'Bond': 15,
            'REIT': 10,
            'Commodity': 5
        }
    
    # Adjust for age (rule of thumb: bond allocation = age)
    if age > 40:
        # Increase bond allocation for older investors
        equity_reduction = min(20, (age - 40) * 0.5)
        allocation['Equity'] = max(20, allocation['Equity'] - equity_reduction)
        allocation['Bond'] = min(70, allocation['Bond'] + equity_reduction)
    
    # Adjust for investment horizon
    if investment_horizon < 10:
        # Shorter horizon - more conservative
        equity_reduction = (10 - investment_horizon) * 2
        allocation['Equity'] = max(20, allocation['Equity'] - equity_reduction)
        allocation['Bond'] = min(70, allocation['Bond'] + equity_reduction)
    
    # Ensure allocations sum to 100%
    total = sum(allocation.values())
    if total != 100:
        # Adjust equity allocation to make total 100%
        allocation['Equity'] += (100 - total)
    
    return allocation

def _select_best_investment(investments: List[Investment], user_profile: UserProfile) -> Investment:
    """Select the best investment from a list based on user profile."""
    
    if len(investments) == 1:
        return investments[0]
    
    # Score investments based on multiple criteria
    scored_investments = []
    
    for investment in investments:
        score = 0
        
        # Expected return score (higher is better)
        score += investment.expected_return * 10
        
        # Risk alignment score
        risk_diff = abs(investment.risk_level - user_profile.get_risk_score())
        score += max(0, 10 - risk_diff)
        
        # Market preference score
        if investment.market == user_profile.preferred_market:
            score += 5
        
        # Compliance score
        if user_profile.is_sharia_compliant and investment.is_sharia_compliant:
            score += 5
        elif user_profile.is_sharia_compliant and not investment.is_sharia_compliant:
            score -= 10  # Heavy penalty for non-compliant investments
        
        # Liquidity score (lower minimum investment is better)
        if investment.min_investment:
            if investment.min_investment <= 1000:
                score += 3
            elif investment.min_investment <= 5000:
                score += 1
        else:
            score += 2  # No minimum is good
        
        scored_investments.append((investment, score))
    
    # Sort by score and return best
    scored_investments.sort(key=lambda x: x[1], reverse=True)
    return scored_investments[0][0]

def _generate_rationale(investment: Investment, user_profile: UserProfile, category: str) -> str:
    """Generate rationale for investment recommendation."""
    
    rationale_parts = []
    
    # Category rationale
    if category == 'Equity':
        rationale_parts.append("Equity allocation for long-term growth potential")
    elif category == 'Bond':
        rationale_parts.append("Bond allocation for stability and income generation")
    elif category == 'REIT':
        rationale_parts.append("REIT allocation for real estate exposure and dividends")
    elif category == 'Commodity':
        rationale_parts.append("Commodity allocation for inflation protection")
    
    # Investment-specific rationale
    if investment.expected_return > 0.08:
        rationale_parts.append("selected for strong expected returns")
    
    if investment.risk_level <= user_profile.get_risk_score():
        rationale_parts.append("aligns with your risk tolerance")
    
    if investment.market == user_profile.preferred_market:
        rationale_parts.append(f"matches your {investment.market} market preference")
    
    if user_profile.is_sharia_compliant and investment.is_sharia_compliant:
        rationale_parts.append("meets Sharia compliance requirements")
    
    return "; ".join(rationale_parts).capitalize()

def _get_default_recommendations(user_profile: UserProfile) -> List[PortfolioRecommendation]:
    """Get default recommendations when no investments are available."""
    
    logger.info("Using default portfolio recommendations")
    
    # Create default investments
    default_investments = _create_default_investments(user_profile)
    
    recommendations = []
    total_investment = user_profile.get_monthly_savings_capacity() * 12
    
    allocation_strategy = _get_allocation_strategy(user_profile)
    
    for i, (category, percentage) in enumerate(allocation_strategy.items()):
        if i < len(default_investments):
            investment = default_investments[i]
            investment.category = category
            
            recommendation = PortfolioRecommendation.from_investment(
                investment=investment,
                allocation_percentage=percentage,
                investment_amount=total_investment * (percentage / 100),
                rationale=f"Default {category.lower()} allocation for diversified portfolio"
            )
            
            recommendations.append(recommendation)
    
    return recommendations

def _create_default_investments(user_profile: UserProfile) -> List[Investment]:
    """Create default investment options."""
    
    market = user_profile.preferred_market
    currency = 'AED' if market == 'UAE' else 'USD'
    
    default_investments = [
        Investment(
            symbol=f"{market}_EQUITY_INDEX",
            name=f"{market} Equity Index Fund",
            category="Equity",
            market=market,
            currency=currency,
            expected_return=0.08,
            risk_level=6,
            is_sharia_compliant=user_profile.is_sharia_compliant,
            description=f"Diversified {market} equity index fund"
        ),
        Investment(
            symbol=f"{market}_BOND_INDEX",
            name=f"{market} Bond Index Fund",
            category="Bond",
            market=market,
            currency=currency,
            expected_return=0.04,
            risk_level=3,
            is_sharia_compliant=user_profile.is_sharia_compliant,
            description=f"{market} government and corporate bond fund"
        ),
        Investment(
            symbol=f"{market}_REIT_INDEX",
            name=f"{market} REIT Fund",
            category="REIT",
            market=market,
            currency=currency,
            expected_return=0.06,
            risk_level=5,
            is_sharia_compliant=user_profile.is_sharia_compliant,
            description=f"{market} real estate investment trust fund"
        ),
        Investment(
            symbol="GOLD_ETF",
            name="Gold ETF",
            category="Commodity",
            market="Global",
            currency=currency,
            expected_return=0.03,
            risk_level=4,
            is_sharia_compliant=True,
            description="Gold exchange-traded fund for inflation protection"
        )
    ]
    
    return default_investments
