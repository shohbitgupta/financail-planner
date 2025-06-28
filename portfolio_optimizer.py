import numpy as np
import pandas as pd
try:
    from scipy.optimize import minimize
except ImportError:
    print("Warning: scipy not installed. Portfolio optimization will be limited.")
    minimize = None
from typing import Dict, List, Tuple, Optional
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

@dataclass
class OptimizationConstraints:
    """Constraints for portfolio optimization"""
    min_weight: float = 0.0
    max_weight: float = 1.0
    max_single_asset: float = 0.3
    min_diversification: int = 5
    sharia_compliant_only: bool = False
    market_preference: Optional[str] = None  # 'UAE', 'US', or None for both
    risk_level_range: Tuple[int, int] = (1, 10)

@dataclass
class InvestorProfile:
    """Investor profile for personalized optimization"""
    age: int
    retirement_age: int
    annual_income: float
    annual_expenses: float
    current_savings: float
    risk_tolerance: int  # 1-10 scale
    investment_horizon: int  # years
    financial_goals: List[str]
    sharia_compliant: bool = False

class PortfolioOptimizer:
    """Modern Portfolio Theory based optimizer with enhanced features"""
    
    def __init__(self, db_path: str = "investment_database.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        
    def get_available_assets(self, constraints: OptimizationConstraints) -> pd.DataFrame:
        """Get available assets based on constraints"""
        query = """
            SELECT i.*, p.one_year_return, p.volatility, p.sharpe_ratio
            FROM instruments i
            LEFT JOIN performance_metrics p ON i.symbol = p.symbol
            WHERE i.risk_level BETWEEN ? AND ?
        """
        params = [constraints.risk_level_range[0], constraints.risk_level_range[1]]
        
        if constraints.sharia_compliant_only:
            query += " AND i.is_sharia_compliant = 1"
            
        if constraints.market_preference:
            query += " AND i.market = ?"
            params.append(constraints.market_preference)
            
        return pd.read_sql_query(query, self.conn, params=params)
    
    def calculate_returns_covariance(self, symbols: List[str], 
                                   lookback_days: int = 252) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate expected returns and covariance matrix"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)
        
        returns_data = []
        
        for symbol in symbols:
            query = """
                SELECT date, close_price 
                FROM historical_data 
                WHERE symbol = ? AND date >= ? AND date <= ?
                ORDER BY date
            """
            data = pd.read_sql_query(
                query, self.conn, 
                params=[symbol, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]
            )
            
            if len(data) < 30:  # Minimum data requirement
                continue
                
            data['returns'] = data['close_price'].pct_change().dropna()
            returns_data.append(data['returns'].values)
        
        if len(returns_data) < 2:
            raise ValueError("Insufficient data for optimization")
        
        # Align data lengths
        min_length = min(len(r) for r in returns_data)
        returns_matrix = np.array([r[-min_length:] for r in returns_data]).T
        
        # Calculate expected returns (annualized)
        expected_returns = np.mean(returns_matrix, axis=0) * 252
        
        # Calculate covariance matrix (annualized)
        cov_matrix = np.cov(returns_matrix.T) * 252
        
        return expected_returns, cov_matrix
    
    def optimize_portfolio(self, investor_profile: InvestorProfile,
                          constraints: OptimizationConstraints,
                          optimization_type: str = 'max_sharpe') -> Dict:
        """
        Optimize portfolio based on investor profile and constraints

        optimization_type: 'max_sharpe', 'min_variance', 'target_return'
        """
        # Check if scipy is available
        if minimize is None:
            raise ValueError("scipy is required for portfolio optimization. Please install: pip install scipy")

        # Get available assets
        assets_df = self.get_available_assets(constraints)

        if len(assets_df) < constraints.min_diversification:
            raise ValueError(f"Insufficient assets for diversification requirement")

        symbols = assets_df['symbol'].tolist()

        # Calculate returns and covariance
        expected_returns, cov_matrix = self.calculate_returns_covariance(symbols)
        
        n_assets = len(symbols)
        
        # Objective functions
        def portfolio_variance(weights):
            return np.dot(weights.T, np.dot(cov_matrix, weights))
        
        def portfolio_return(weights):
            return np.dot(weights, expected_returns)
        
        def negative_sharpe(weights):
            ret = portfolio_return(weights)
            vol = np.sqrt(portfolio_variance(weights))
            return -(ret - 0.02) / vol  # Assuming 2% risk-free rate
        
        # Constraints
        constraint_list = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # Weights sum to 1
        ]
        
        # Bounds
        bounds = tuple((constraints.min_weight, 
                       min(constraints.max_weight, constraints.max_single_asset)) 
                      for _ in range(n_assets))
        
        # Initial guess (equal weights)
        x0 = np.array([1/n_assets] * n_assets)
        
        # Optimize based on type
        if optimization_type == 'max_sharpe':
            result = minimize(negative_sharpe, x0, method='SLSQP', 
                            bounds=bounds, constraints=constraint_list)
        elif optimization_type == 'min_variance':
            result = minimize(portfolio_variance, x0, method='SLSQP',
                            bounds=bounds, constraints=constraint_list)
        else:  # target_return
            target_return = self._calculate_target_return(investor_profile)
            constraint_list.append({
                'type': 'eq', 
                'fun': lambda x: portfolio_return(x) - target_return
            })
            result = minimize(portfolio_variance, x0, method='SLSQP',
                            bounds=bounds, constraints=constraint_list)
        
        if not result.success:
            raise ValueError("Optimization failed to converge")
        
        optimal_weights = result.x
        
        # Calculate portfolio metrics
        portfolio_return_val = portfolio_return(optimal_weights)
        portfolio_variance_val = portfolio_variance(optimal_weights)
        portfolio_volatility = np.sqrt(portfolio_variance_val)
        sharpe_ratio = (portfolio_return_val - 0.02) / portfolio_volatility
        
        # Create allocation dictionary
        allocation = {}
        for i, symbol in enumerate(symbols):
            if optimal_weights[i] > 0.001:  # Only include significant allocations
                allocation[symbol] = {
                    'weight': round(optimal_weights[i], 4),
                    'asset_info': assets_df[assets_df['symbol'] == symbol].iloc[0].to_dict()
                }
        
        return {
            'allocation': allocation,
            'expected_return': round(portfolio_return_val, 4),
            'volatility': round(portfolio_volatility, 4),
            'sharpe_ratio': round(sharpe_ratio, 4),
            'optimization_type': optimization_type,
            'total_assets': len(allocation),
            'investor_profile': investor_profile,
            'constraints': constraints
        }
    
    def _calculate_target_return(self, investor_profile: InvestorProfile) -> float:
        """Calculate target return based on investor profile"""
        # Age-based equity allocation (100 - age rule, adjusted)
        equity_allocation = max(0.3, min(0.9, (120 - investor_profile.age) / 100))
        
        # Risk tolerance adjustment
        risk_adjustment = (investor_profile.risk_tolerance - 5) * 0.01
        
        # Base expected returns
        equity_return = 0.10  # 10% expected equity return
        bond_return = 0.04   # 4% expected bond return
        
        target_return = (equity_allocation * equity_return + 
                        (1 - equity_allocation) * bond_return + 
                        risk_adjustment)
        
        return max(0.03, min(0.15, target_return))  # Bound between 3% and 15%
    
    def generate_efficient_frontier(self, investor_profile: InvestorProfile,
                                  constraints: OptimizationConstraints,
                                  num_portfolios: int = 50) -> pd.DataFrame:
        """Generate efficient frontier data"""
        assets_df = self.get_available_assets(constraints)
        symbols = assets_df['symbol'].tolist()
        expected_returns, cov_matrix = self.calculate_returns_covariance(symbols)
        
        # Calculate range of target returns
        min_return = np.min(expected_returns)
        max_return = np.max(expected_returns)
        target_returns = np.linspace(min_return, max_return, num_portfolios)
        
        efficient_portfolios = []
        
        for target_ret in target_returns:
            try:
                # Temporarily modify constraints for target return
                temp_constraints = constraints
                result = self.optimize_portfolio(
                    investor_profile, temp_constraints, 'target_return'
                )
                
                efficient_portfolios.append({
                    'target_return': target_ret,
                    'expected_return': result['expected_return'],
                    'volatility': result['volatility'],
                    'sharpe_ratio': result['sharpe_ratio']
                })
            except:
                continue
        
        return pd.DataFrame(efficient_portfolios)
    
    def close(self):
        """Close database connection"""
        self.conn.close()

# Example usage and testing
def demo_portfolio_optimizer():
    """Demonstrate portfolio optimization capabilities"""
    
    # Create sample investor profile
    investor = InvestorProfile(
        age=35,
        retirement_age=65,
        annual_income=100000,
        annual_expenses=60000,
        current_savings=50000,
        risk_tolerance=7,
        investment_horizon=30,
        financial_goals=["Retirement", "House Purchase"],
        sharia_compliant=False
    )
    
    # Create optimization constraints
    constraints = OptimizationConstraints(
        max_single_asset=0.25,
        min_diversification=5,
        sharia_compliant_only=False,
        risk_level_range=(3, 8)
    )
    
    optimizer = PortfolioOptimizer()
    
    try:
        # Optimize for maximum Sharpe ratio
        result = optimizer.optimize_portfolio(investor, constraints, 'max_sharpe')
        
        print("=== OPTIMAL PORTFOLIO ===")
        print(f"Expected Return: {result['expected_return']:.2%}")
        print(f"Volatility: {result['volatility']:.2%}")
        print(f"Sharpe Ratio: {result['sharpe_ratio']:.3f}")
        print(f"Number of Assets: {result['total_assets']}")
        
        print("\n=== ALLOCATION ===")
        for symbol, details in result['allocation'].items():
            print(f"{symbol}: {details['weight']:.1%} - {details['asset_info']['name']}")
            
    except Exception as e:
        print(f"Optimization error: {e}")
    
    finally:
        optimizer.close()

if __name__ == "__main__":
    demo_portfolio_optimizer()
