#!/usr/bin/env python3
"""
Database Refresh Script for Financial Planner AI Agent

This script refreshes the investment database with enhanced historical data
to provide more realistic and comprehensive financial analysis.
"""

import sys
import os
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from investment_database import InvestmentDatabase

def main():
    """Refresh the investment database with enhanced data"""
    
    print("🏦 FINANCIAL PLANNER AI - DATABASE REFRESH")
    print("="*50)
    
    try:
        # Initialize database
        print("📊 Initializing investment database...")
        db = InvestmentDatabase()
        
        # Show current database status
        print("\n📈 Current Database Status:")
        summary = db.get_data_summary()
        print(f"  • Total Instruments: {summary['total_instruments']}")
        print(f"  • UAE Instruments: {summary['uae_instruments']}")
        print(f"  • US Instruments: {summary['us_instruments']}")
        print(f"  • Sharia-Compliant: {summary['sharia_compliant']}")
        print(f"  • Total Data Points: {summary['total_data_points']:,}")
        print(f"  • Average Data per Instrument: {summary['avg_data_per_instrument']:.0f}")
        if summary['date_range'][0]:
            print(f"  • Date Range: {summary['date_range'][0]} to {summary['date_range'][1]}")
        
        # Refresh database with 7 years of data
        print(f"\n🔄 Refreshing database with enhanced historical data...")
        db.refresh_database(years=7)
        
        # Show updated status
        print("\n📈 Updated Database Status:")
        summary = db.get_data_summary()
        print(f"  • Total Instruments: {summary['total_instruments']}")
        print(f"  • Total Data Points: {summary['total_data_points']:,}")
        print(f"  • Average Data per Instrument: {summary['avg_data_per_instrument']:.0f}")
        print(f"  • Date Range: {summary['date_range'][0]} to {summary['date_range'][1]}")
        
        # Test portfolio optimization with enhanced data
        print(f"\n🎯 Testing Portfolio Optimization...")
        test_portfolio_optimization(db)
        
        # Show sample performance metrics
        print(f"\n📊 Sample Performance Metrics:")
        show_sample_metrics(db)
        
        db.close()
        
        print(f"\n✅ Database refresh completed successfully!")
        print(f"🚀 Your financial planner AI now has enhanced data for better recommendations.")
        
    except Exception as e:
        print(f"\n❌ Error during database refresh: {e}")
        print("Please check your environment and try again.")
        return 1
    
    return 0

def test_portfolio_optimization(db):
    """Test portfolio optimization with the enhanced database"""
    try:
        from portfolio_optimizer import PortfolioOptimizer, InvestorProfile, OptimizationConstraints
        
        # Create test investor profile
        investor = InvestorProfile(
            age=35, retirement_age=65, annual_income=80000, annual_expenses=60000,
            current_savings=50000, risk_tolerance=6, investment_horizon=30,
            financial_goals=["Retirement"], sharia_compliant=False
        )
        
        # Create constraints
        constraints = OptimizationConstraints(
            risk_level_range=(4, 8), max_single_asset=0.25
        )
        
        # Test optimization
        optimizer = PortfolioOptimizer()
        result = optimizer.optimize_portfolio(investor, constraints, 'max_sharpe')
        
        print(f"  ✅ Portfolio optimization successful!")
        print(f"  • Expected Return: {result['expected_return']:.1%}")
        print(f"  • Volatility: {result['volatility']:.1%}")
        print(f"  • Sharpe Ratio: {result['sharpe_ratio']:.2f}")
        print(f"  • Assets in Portfolio: {result['total_assets']}")
        
        optimizer.close()
        
    except Exception as e:
        print(f"  ⚠️  Portfolio optimization test failed: {e}")

def show_sample_metrics(db):
    """Show sample performance metrics from the database"""
    try:
        # Get performance metrics for a few instruments
        sample_symbols = ['SPY', 'FAB', 'EMAAR', 'QQQ', 'UAEETF']
        
        for symbol in sample_symbols:
            metrics = db.get_performance_metrics(symbol)
            if not metrics.empty:
                m = metrics.iloc[0]
                print(f"  • {symbol}:")
                print(f"    - 1Y Return: {m['one_year_return']:.1%}" if m['one_year_return'] else "    - 1Y Return: N/A")
                print(f"    - Volatility: {m['volatility']:.1%}" if m['volatility'] else "    - Volatility: N/A")
                print(f"    - Sharpe Ratio: {m['sharpe_ratio']:.2f}" if m['sharpe_ratio'] else "    - Sharpe Ratio: N/A")
            else:
                print(f"  • {symbol}: No metrics available")
                
    except Exception as e:
        print(f"  ⚠️  Error showing sample metrics: {e}")

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
