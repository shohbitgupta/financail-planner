import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import random

@dataclass
class FinancialGoal:
    """Represents a financial goal"""
    name: str
    target_amount: float
    target_date: datetime
    priority: int  # 1-5 scale
    inflation_adjusted: bool = True

@dataclass
class RetirementPlan:
    """Retirement planning parameters"""
    current_age: int
    retirement_age: int
    current_savings: float
    monthly_contribution: float
    expected_return: float
    inflation_rate: float = 0.03
    replacement_ratio: float = 0.8  # 80% of pre-retirement income
    life_expectancy: int = 85

class FinancialCalculator:
    """Comprehensive financial planning calculator with Monte Carlo simulations"""
    
    def __init__(self):
        self.inflation_rate = 0.03  # Default 3% inflation
        
    def calculate_retirement_needs(self, retirement_plan: RetirementPlan, 
                                 current_annual_income: float) -> Dict:
        """Calculate retirement funding requirements"""
        
        years_to_retirement = retirement_plan.retirement_age - retirement_plan.current_age
        years_in_retirement = retirement_plan.life_expectancy - retirement_plan.retirement_age
        
        # Calculate required annual income in retirement (inflation-adjusted)
        required_annual_income = current_annual_income * retirement_plan.replacement_ratio
        future_required_income = required_annual_income * (1 + retirement_plan.inflation_rate) ** years_to_retirement
        
        # Calculate total retirement corpus needed (present value of annuity)
        real_return = (retirement_plan.expected_return - retirement_plan.inflation_rate) / (1 + retirement_plan.inflation_rate)
        
        if real_return > 0:
            retirement_corpus = future_required_income * (1 - (1 + real_return) ** -years_in_retirement) / real_return
        else:
            retirement_corpus = future_required_income * years_in_retirement
        
        # Calculate future value of current savings
        future_value_current_savings = retirement_plan.current_savings * (1 + retirement_plan.expected_return) ** years_to_retirement
        
        # Calculate future value of monthly contributions
        monthly_rate = retirement_plan.expected_return / 12
        months_to_retirement = years_to_retirement * 12
        
        if monthly_rate > 0:
            future_value_contributions = retirement_plan.monthly_contribution * \
                ((1 + monthly_rate) ** months_to_retirement - 1) / monthly_rate
        else:
            future_value_contributions = retirement_plan.monthly_contribution * months_to_retirement
        
        total_accumulated = future_value_current_savings + future_value_contributions
        shortfall = max(0, retirement_corpus - total_accumulated)
        
        # Calculate required additional monthly savings
        if shortfall > 0 and monthly_rate > 0:
            required_additional_monthly = shortfall / (((1 + monthly_rate) ** months_to_retirement - 1) / monthly_rate)
        else:
            required_additional_monthly = shortfall / months_to_retirement if months_to_retirement > 0 else 0
        
        return {
            'retirement_corpus_needed': round(retirement_corpus, 2),
            'future_required_annual_income': round(future_required_income, 2),
            'current_savings_future_value': round(future_value_current_savings, 2),
            'contributions_future_value': round(future_value_contributions, 2),
            'total_accumulated': round(total_accumulated, 2),
            'shortfall': round(shortfall, 2),
            'required_additional_monthly_savings': round(required_additional_monthly, 2),
            'years_to_retirement': years_to_retirement,
            'years_in_retirement': years_in_retirement,
            'is_on_track': shortfall <= 0
        }
    
    def calculate_goal_funding(self, goal: FinancialGoal, 
                             current_savings: float = 0,
                             monthly_contribution: float = 0,
                             expected_return: float = 0.07) -> Dict:
        """Calculate funding requirements for a specific financial goal"""
        
        years_to_goal = (goal.target_date - datetime.now()).days / 365.25
        
        if years_to_goal <= 0:
            return {'error': 'Goal date must be in the future'}
        
        # Adjust target amount for inflation if required
        target_amount = goal.target_amount
        if goal.inflation_adjusted:
            target_amount = goal.target_amount * (1 + self.inflation_rate) ** years_to_goal
        
        # Calculate future value of current savings
        future_value_current = current_savings * (1 + expected_return) ** years_to_goal
        
        # Calculate future value of monthly contributions
        monthly_rate = expected_return / 12
        months_to_goal = years_to_goal * 12
        
        if monthly_rate > 0:
            future_value_contributions = monthly_contribution * \
                ((1 + monthly_rate) ** months_to_goal - 1) / monthly_rate
        else:
            future_value_contributions = monthly_contribution * months_to_goal
        
        total_accumulated = future_value_current + future_value_contributions
        shortfall = max(0, target_amount - total_accumulated)
        
        # Calculate required monthly savings to meet goal
        if shortfall > 0 and monthly_rate > 0:
            required_monthly = shortfall / (((1 + monthly_rate) ** months_to_goal - 1) / monthly_rate)
        else:
            required_monthly = shortfall / months_to_goal if months_to_goal > 0 else 0
        
        return {
            'goal_name': goal.name,
            'target_amount': round(target_amount, 2),
            'years_to_goal': round(years_to_goal, 1),
            'current_savings_future_value': round(future_value_current, 2),
            'contributions_future_value': round(future_value_contributions, 2),
            'total_accumulated': round(total_accumulated, 2),
            'shortfall': round(shortfall, 2),
            'required_monthly_savings': round(required_monthly, 2),
            'probability_of_success': self._calculate_success_probability(
                target_amount, total_accumulated, years_to_goal, expected_return
            )
        }
    
    def monte_carlo_retirement_simulation(self, retirement_plan: RetirementPlan,
                                        current_annual_income: float,
                                        num_simulations: int = 1000,
                                        return_volatility: float = 0.15) -> Dict:
        """Run Monte Carlo simulation for retirement planning"""
        
        years_to_retirement = retirement_plan.retirement_age - retirement_plan.current_age
        years_in_retirement = retirement_plan.life_expectancy - retirement_plan.retirement_age
        
        success_count = 0
        final_balances = []
        
        for _ in range(num_simulations):
            # Accumulation phase
            balance = retirement_plan.current_savings
            
            for year in range(years_to_retirement):
                # Random return for this year
                annual_return = np.random.normal(retirement_plan.expected_return, return_volatility)
                balance = balance * (1 + annual_return) + retirement_plan.monthly_contribution * 12
            
            # Withdrawal phase
            required_annual_income = current_annual_income * retirement_plan.replacement_ratio
            required_annual_income *= (1 + retirement_plan.inflation_rate) ** years_to_retirement
            
            for year in range(years_in_retirement):
                annual_return = np.random.normal(retirement_plan.expected_return, return_volatility)
                balance = balance * (1 + annual_return) - required_annual_income
                required_annual_income *= (1 + retirement_plan.inflation_rate)
                
                if balance <= 0:
                    break
            
            if balance > 0:
                success_count += 1
            
            final_balances.append(balance)
        
        success_rate = success_count / num_simulations
        
        return {
            'success_rate': round(success_rate, 3),
            'median_final_balance': round(np.median(final_balances), 2),
            'percentile_10': round(np.percentile(final_balances, 10), 2),
            'percentile_90': round(np.percentile(final_balances, 90), 2),
            'simulations_run': num_simulations,
            'recommendation': self._get_retirement_recommendation(success_rate)
        }
    
    def calculate_emergency_fund(self, monthly_expenses: float, 
                               job_stability: str = 'stable',
                               dependents: int = 0) -> Dict:
        """Calculate recommended emergency fund size"""
        
        base_months = {
            'very_stable': 3,
            'stable': 6,
            'unstable': 9,
            'very_unstable': 12
        }
        
        months_needed = base_months.get(job_stability, 6)
        
        # Adjust for dependents
        months_needed += dependents * 1
        
        emergency_fund_target = monthly_expenses * months_needed
        
        return {
            'recommended_months': months_needed,
            'target_amount': round(emergency_fund_target, 2),
            'monthly_expenses': monthly_expenses,
            'job_stability': job_stability,
            'dependents': dependents
        }
    
    def calculate_debt_payoff(self, debts: List[Dict], 
                            extra_payment: float = 0,
                            strategy: str = 'avalanche') -> Dict:
        """
        Calculate debt payoff strategy
        debts: List of {'name': str, 'balance': float, 'rate': float, 'min_payment': float}
        strategy: 'avalanche' (highest rate first) or 'snowball' (lowest balance first)
        """
        
        if strategy == 'avalanche':
            sorted_debts = sorted(debts, key=lambda x: x['rate'], reverse=True)
        else:  # snowball
            sorted_debts = sorted(debts, key=lambda x: x['balance'])
        
        total_balance = sum(debt['balance'] for debt in debts)
        total_min_payment = sum(debt['min_payment'] for debt in debts)
        total_payment = total_min_payment + extra_payment
        
        payoff_schedule = []
        remaining_debts = [debt.copy() for debt in sorted_debts]
        month = 0
        
        while remaining_debts:
            month += 1
            available_extra = extra_payment
            
            # Make minimum payments
            for debt in remaining_debts:
                debt['balance'] -= debt['min_payment']
                debt['balance'] = max(0, debt['balance'])
            
            # Apply extra payment to priority debt
            if remaining_debts and available_extra > 0:
                priority_debt = remaining_debts[0]
                payment = min(available_extra, priority_debt['balance'])
                priority_debt['balance'] -= payment
                available_extra -= payment
            
            # Remove paid-off debts
            remaining_debts = [debt for debt in remaining_debts if debt['balance'] > 0]
            
            if month > 600:  # Safety break (50 years)
                break
        
        total_interest = month * total_min_payment + extra_payment * month - total_balance
        
        return {
            'months_to_payoff': month,
            'years_to_payoff': round(month / 12, 1),
            'total_interest_paid': round(max(0, total_interest), 2),
            'total_payments': round(month * total_payment, 2),
            'strategy_used': strategy,
            'monthly_payment': round(total_payment, 2)
        }
    
    def _calculate_success_probability(self, target: float, current_path: float, 
                                     years: float, expected_return: float) -> float:
        """Calculate probability of reaching financial goal"""
        if years <= 0:
            return 1.0 if current_path >= target else 0.0
        
        # Simple probability model based on expected growth vs required growth
        required_return = (target / current_path) ** (1/years) - 1 if current_path > 0 else float('inf')
        
        if required_return <= expected_return:
            return min(0.95, 0.5 + (expected_return - required_return) * 2)
        else:
            return max(0.05, 0.5 - (required_return - expected_return) * 2)
    
    def _get_retirement_recommendation(self, success_rate: float) -> str:
        """Get recommendation based on Monte Carlo success rate"""
        if success_rate >= 0.9:
            return "Excellent! You're on track for a comfortable retirement."
        elif success_rate >= 0.75:
            return "Good progress. Consider increasing contributions slightly."
        elif success_rate >= 0.5:
            return "Moderate risk. Increase savings or adjust expectations."
        else:
            return "High risk. Significant changes needed to retirement plan."

# Example usage
def demo_financial_calculator():
    """Demonstrate financial calculator capabilities"""
    
    calc = FinancialCalculator()
    
    # Retirement planning example
    retirement_plan = RetirementPlan(
        current_age=30,
        retirement_age=65,
        current_savings=50000,
        monthly_contribution=1000,
        expected_return=0.08
    )
    
    retirement_analysis = calc.calculate_retirement_needs(retirement_plan, 80000)
    print("=== RETIREMENT ANALYSIS ===")
    for key, value in retirement_analysis.items():
        print(f"{key}: {value}")
    
    # Monte Carlo simulation
    print("\n=== MONTE CARLO SIMULATION ===")
    mc_results = calc.monte_carlo_retirement_simulation(retirement_plan, 80000)
    for key, value in mc_results.items():
        print(f"{key}: {value}")
    
    # Goal planning example
    house_goal = FinancialGoal(
        name="House Down Payment",
        target_amount=100000,
        target_date=datetime(2029, 1, 1),
        priority=1
    )
    
    goal_analysis = calc.calculate_goal_funding(house_goal, 20000, 800)
    print("\n=== GOAL ANALYSIS ===")
    for key, value in goal_analysis.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    demo_financial_calculator()
