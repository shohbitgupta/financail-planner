"""
Financial calculation utilities.
"""
import math
from typing import Dict, Any, List, Optional

class FinancialCalculator:
    """Financial calculation utilities for planning and analysis."""
    
    def calculate_future_value(self, present_value: float, monthly_payment: float, 
                             annual_rate: float, years: int) -> float:
        """Calculate future value with compound interest and monthly payments."""
        if annual_rate <= 0 or years <= 0:
            return present_value + (monthly_payment * 12 * years)
        
        monthly_rate = annual_rate / 12
        months = years * 12
        
        # Future value of present value
        fv_present = present_value * ((1 + annual_rate) ** years)
        
        # Future value of annuity (monthly payments)
        if monthly_payment > 0:
            fv_annuity = monthly_payment * (((1 + monthly_rate) ** months - 1) / monthly_rate)
        else:
            fv_annuity = 0
        
        return fv_present + fv_annuity
    
    def calculate_monthly_payment_needed(self, future_value: float, 
                                       annual_rate: float, years: int) -> float:
        """Calculate monthly payment needed to reach future value."""
        if years <= 0:
            return future_value / 12
        
        if annual_rate <= 0:
            return future_value / (12 * years)
        
        monthly_rate = annual_rate / 12
        months = years * 12
        
        # PMT formula for annuity
        payment = future_value * monthly_rate / ((1 + monthly_rate) ** months - 1)
        return payment
    
    def calculate_retirement_corpus(self, annual_expenses: float, 
                                  withdrawal_rate: float = 0.04) -> float:
        """Calculate retirement corpus needed using withdrawal rate."""
        return annual_expenses / withdrawal_rate
    
    def calculate_sip_returns(self, monthly_investment: float, annual_rate: float, 
                            years: int) -> Dict[str, float]:
        """Calculate SIP (Systematic Investment Plan) returns."""
        if annual_rate <= 0 or years <= 0:
            total_invested = monthly_investment * 12 * years
            return {
                'total_invested': total_invested,
                'maturity_value': total_invested,
                'total_returns': 0,
                'absolute_return': 0
            }
        
        monthly_rate = annual_rate / 12
        months = years * 12
        
        # Future value of SIP
        maturity_value = monthly_investment * (((1 + monthly_rate) ** months - 1) / monthly_rate)
        total_invested = monthly_investment * months
        total_returns = maturity_value - total_invested
        absolute_return = (total_returns / total_invested) * 100 if total_invested > 0 else 0
        
        return {
            'total_invested': total_invested,
            'maturity_value': maturity_value,
            'total_returns': total_returns,
            'absolute_return': absolute_return
        }
    
    def calculate_compound_annual_growth_rate(self, initial_value: float, 
                                            final_value: float, years: int) -> float:
        """Calculate CAGR (Compound Annual Growth Rate)."""
        if initial_value <= 0 or final_value <= 0 or years <= 0:
            return 0.0
        
        cagr = ((final_value / initial_value) ** (1 / years)) - 1
        return cagr * 100
    
    def calculate_portfolio_risk(self, weights: List[float], 
                               returns: List[float], 
                               volatilities: List[float],
                               correlations: Optional[List[List[float]]] = None) -> Dict[str, float]:
        """Calculate portfolio risk metrics."""
        if len(weights) != len(returns) or len(weights) != len(volatilities):
            raise ValueError("Weights, returns, and volatilities must have same length")
        
        # Portfolio expected return
        portfolio_return = sum(w * r for w, r in zip(weights, returns))
        
        # Portfolio volatility (simplified without correlation matrix)
        if correlations is None:
            # Assume zero correlation for simplicity
            portfolio_volatility = math.sqrt(sum((w * v) ** 2 for w, v in zip(weights, volatilities)))
        else:
            # Use correlation matrix
            variance = 0
            for i in range(len(weights)):
                for j in range(len(weights)):
                    variance += weights[i] * weights[j] * volatilities[i] * volatilities[j] * correlations[i][j]
            portfolio_volatility = math.sqrt(variance)
        
        # Sharpe ratio (assuming risk-free rate of 3%)
        risk_free_rate = 0.03
        sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0
        
        return {
            'expected_return': portfolio_return,
            'volatility': portfolio_volatility,
            'sharpe_ratio': sharpe_ratio
        }
    
    def calculate_emergency_fund_needed(self, monthly_expenses: float, 
                                      months: int = 6) -> float:
        """Calculate emergency fund requirement."""
        return monthly_expenses * months
    
    def calculate_insurance_coverage(self, annual_income: float, 
                                   dependents: int = 0,
                                   debt: float = 0) -> Dict[str, float]:
        """Calculate recommended insurance coverage."""
        # Basic life insurance: 10x annual income + debt
        life_insurance = (annual_income * 10) + debt
        
        # Additional coverage for dependents
        if dependents > 0:
            life_insurance += dependents * annual_income * 2
        
        # Health insurance: Based on income bracket
        if annual_income < 50000:
            health_insurance = 500000  # 5 Lakh
        elif annual_income < 100000:
            health_insurance = 1000000  # 10 Lakh
        else:
            health_insurance = 2000000  # 20 Lakh
        
        return {
            'life_insurance': life_insurance,
            'health_insurance': health_insurance,
            'total_premium_estimate': (life_insurance * 0.005) + (health_insurance * 0.01)
        }
    
    def calculate_tax_savings(self, annual_income: float, 
                            investments_80c: float = 0,
                            other_deductions: float = 0) -> Dict[str, float]:
        """Calculate tax savings (simplified Indian tax structure)."""
        # Basic exemption limit
        exemption_limit = 250000
        
        # Total deductions
        total_deductions = min(investments_80c, 150000) + other_deductions
        
        # Taxable income
        taxable_income = max(0, annual_income - exemption_limit - total_deductions)
        
        # Tax calculation (simplified slabs)
        tax = 0
        if taxable_income > 1000000:
            tax += (taxable_income - 1000000) * 0.30
            taxable_income = 1000000
        if taxable_income > 500000:
            tax += (taxable_income - 500000) * 0.20
            taxable_income = 500000
        if taxable_income > 0:
            tax += taxable_income * 0.05
        
        # Tax savings from 80C investments
        tax_savings = min(investments_80c, 150000) * 0.20  # Assuming 20% tax bracket
        
        return {
            'taxable_income': annual_income - exemption_limit - total_deductions,
            'total_tax': tax,
            'tax_savings': tax_savings,
            'effective_tax_rate': (tax / annual_income) * 100 if annual_income > 0 else 0
        }
    
    def monte_carlo_simulation(self, initial_amount: float, 
                             monthly_contribution: float,
                             expected_return: float, 
                             volatility: float,
                             years: int, 
                             simulations: int = 1000) -> Dict[str, Any]:
        """Run Monte Carlo simulation for investment projections."""
        import random
        
        results = []
        
        for _ in range(simulations):
            amount = initial_amount
            for year in range(years):
                # Generate random return based on normal distribution
                annual_return = random.normalvariate(expected_return, volatility)
                amount = amount * (1 + annual_return) + (monthly_contribution * 12)
            results.append(amount)
        
        # Calculate statistics
        results.sort()
        
        return {
            'mean': sum(results) / len(results),
            'median': results[len(results) // 2],
            'percentile_10': results[int(len(results) * 0.1)],
            'percentile_25': results[int(len(results) * 0.25)],
            'percentile_75': results[int(len(results) * 0.75)],
            'percentile_90': results[int(len(results) * 0.9)],
            'best_case': max(results),
            'worst_case': min(results),
            'probability_of_success': len([r for r in results if r >= initial_amount * 2]) / len(results)
        }
