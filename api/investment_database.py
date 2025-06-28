import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import sqlite3
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import random

@dataclass
class InvestmentInstrument:
    """Data class for investment instruments"""
    symbol: str
    name: str
    category: str
    market: str  # UAE or US
    currency: str
    risk_level: int  # 1-10 scale
    min_investment: float
    expense_ratio: Optional[float]
    dividend_yield: Optional[float]
    is_sharia_compliant: bool
    description: str
    
class InvestmentDatabase:
    """Investment Instruments Database with Historical Data"""
    
    def __init__(self, db_path: str = "investment_database.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()
        self.populate_instruments()
        self.generate_historical_data()
    
    def create_tables(self):
        """Create database tables"""
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS instruments (
                symbol TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                market TEXT NOT NULL,
                currency TEXT NOT NULL,
                risk_level INTEGER NOT NULL,
                min_investment REAL NOT NULL,
                expense_ratio REAL,
                dividend_yield REAL,
                is_sharia_compliant BOOLEAN NOT NULL,
                description TEXT
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS historical_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                date TEXT NOT NULL,
                open_price REAL NOT NULL,
                high_price REAL NOT NULL,
                low_price REAL NOT NULL,
                close_price REAL NOT NULL,
                volume INTEGER,
                adjusted_close REAL,
                FOREIGN KEY (symbol) REFERENCES instruments (symbol),
                UNIQUE(symbol, date)
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                symbol TEXT PRIMARY KEY,
                ytd_return REAL,
                one_year_return REAL,
                three_year_return REAL,
                five_year_return REAL,
                volatility REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                FOREIGN KEY (symbol) REFERENCES instruments (symbol)
            )
        ''')
        
        self.conn.commit()
    
    def populate_instruments(self):
        """Populate the database with investment instruments"""
        
        # UAE Market Instruments
        uae_instruments = [
            # UAE Banks
            InvestmentInstrument("FAB", "First Abu Dhabi Bank", "Banking", "UAE", "AED", 6, 1000, None, 4.2, True, "Largest bank in UAE"),
            InvestmentInstrument("ENBD", "Emirates NBD Bank", "Banking", "UAE", "AED", 6, 1000, None, 3.8, True, "Leading banking group in the region"),
            InvestmentInstrument("ADCB", "Abu Dhabi Commercial Bank", "Banking", "UAE", "AED", 6, 1000, None, 4.5, True, "Major commercial bank in UAE"),
            
            # UAE Real Estate
            InvestmentInstrument("EMAAR", "Emaar Properties", "Real Estate", "UAE", "AED", 7, 1000, None, 2.5, True, "Leading real estate developer"),
            InvestmentInstrument("ALDAR", "Aldar Properties", "Real Estate", "UAE", "AED", 7, 1000, None, 3.1, True, "Abu Dhabi-based property developer"),
            
            # UAE Telecommunications
            InvestmentInstrument("ETISALAT", "Emirates Telecommunications", "Telecommunications", "UAE", "AED", 5, 1000, None, 5.2, True, "Leading telecom provider"),
            InvestmentInstrument("DU", "Emirates Integrated Telecommunications", "Telecommunications", "UAE", "AED", 6, 1000, None, 4.8, True, "Major telecom operator"),
            
            # UAE ETFs and Funds
            InvestmentInstrument("UAEETF", "UAE Equity ETF", "ETF", "UAE", "AED", 6, 5000, 0.75, 2.8, True, "Tracks UAE stock market index"),
            InvestmentInstrument("GULFFUND", "Gulf Equity Fund", "Mutual Fund", "UAE", "AED", 7, 10000, 1.25, 2.2, True, "Invests in GCC markets"),
            
            # UAE Bonds
            InvestmentInstrument("UAEGOV5Y", "UAE Government Bond 5Y", "Government Bond", "UAE", "AED", 2, 10000, None, 3.5, True, "5-year UAE government bond"),
            InvestmentInstrument("UAEGOV10Y", "UAE Government Bond 10Y", "Government Bond", "UAE", "AED", 3, 10000, None, 4.2, True, "10-year UAE government bond"),
            
            # Islamic Instruments
            InvestmentInstrument("SUKUK5Y", "UAE Sukuk 5Y", "Islamic Bond", "UAE", "AED", 3, 5000, None, 3.8, True, "5-year Sharia-compliant bond"),
            InvestmentInstrument("ISLAMICFUND", "UAE Islamic Equity Fund", "Islamic Fund", "UAE", "AED", 6, 5000, 1.5, 2.5, True, "Sharia-compliant equity fund"),
            
            # Commodities (Gold popular in UAE)
            InvestmentInstrument("GOLD", "Gold Investment", "Commodity", "UAE", "USD", 4, 1000, 0.5, 0, True, "Physical gold investment"),
            InvestmentInstrument("SILVR", "Silver Investment", "Commodity", "UAE", "USD", 5, 500, 0.6, 0, True, "Physical silver investment"),
        ]
        
        # US Market Instruments
        us_instruments = [
            # US ETFs
            InvestmentInstrument("SPY", "SPDR S&P 500 ETF", "ETF", "US", "USD", 6, 100, 0.09, 1.3, False, "Tracks S&P 500 index"),
            InvestmentInstrument("QQQ", "Invesco QQQ ETF", "ETF", "US", "USD", 8, 100, 0.20, 0.5, False, "Tracks Nasdaq-100 index"),
            InvestmentInstrument("VTI", "Vanguard Total Stock Market ETF", "ETF", "US", "USD", 7, 100, 0.03, 1.4, False, "Total US stock market"),
            InvestmentInstrument("VEA", "Vanguard Developed Markets ETF", "ETF", "US", "USD", 7, 100, 0.05, 2.1, False, "International developed markets"),
            InvestmentInstrument("VWO", "Vanguard Emerging Markets ETF", "ETF", "US", "USD", 8, 100, 0.10, 2.8, False, "Emerging markets"),
            
            # US Bonds
            InvestmentInstrument("TLT", "iShares 20+ Year Treasury Bond ETF", "Bond ETF", "US", "USD", 4, 100, 0.15, 2.4, False, "Long-term US Treasury bonds"),
            InvestmentInstrument("IEF", "iShares 7-10 Year Treasury Bond ETF", "Bond ETF", "US", "USD", 3, 100, 0.15, 2.1, False, "Intermediate-term Treasury bonds"),
            InvestmentInstrument("AGG", "iShares Core US Aggregate Bond ETF", "Bond ETF", "US", "USD", 3, 100, 0.03, 2.2, False, "US aggregate bond market"),
            
            # US Individual Stocks (Blue Chip)
            InvestmentInstrument("AAPL", "Apple Inc.", "Technology Stock", "US", "USD", 7, 50, None, 0.4, False, "Technology giant"),
            InvestmentInstrument("MSFT", "Microsoft Corporation", "Technology Stock", "US", "USD", 6, 50, None, 0.7, False, "Software and cloud services"),
            InvestmentInstrument("GOOGL", "Alphabet Inc.", "Technology Stock", "US", "USD", 7, 50, None, 0, False, "Search and advertising"),
            InvestmentInstrument("AMZN", "Amazon.com Inc.", "Consumer Stock", "US", "USD", 8, 50, None, 0, False, "E-commerce and cloud"),
            InvestmentInstrument("TSLA", "Tesla Inc.", "Automotive Stock", "US", "USD", 9, 50, None, 0, False, "Electric vehicles"),
            
            # US Mutual Funds
            InvestmentInstrument("VTSAX", "Vanguard Total Stock Market Index Fund", "Mutual Fund", "US", "USD", 7, 3000, 0.04, 1.3, False, "Total stock market index fund"),
            InvestmentInstrument("VTIAX", "Vanguard Total International Stock Index Fund", "Mutual Fund", "US", "USD", 8, 3000, 0.11, 2.2, False, "International stock index fund"),
            
            # Alternative Investments
            InvestmentInstrument("VNQ", "Vanguard Real Estate ETF", "REIT ETF", "US", "USD", 6, 100, 0.12, 3.5, False, "US real estate investment trusts"),
            InvestmentInstrument("GLD", "SPDR Gold Shares", "Commodity ETF", "US", "USD", 4, 100, 0.40, 0, True, "Gold commodity ETF"),
            InvestmentInstrument("SLV", "iShares Silver Trust", "Commodity ETF", "US", "USD", 5, 100, 0.50, 0, True, "Silver commodity ETF"),
        ]
        
        # Insert all instruments
        all_instruments = uae_instruments + us_instruments
        
        for instrument in all_instruments:
            try:
                self.conn.execute('''
                    INSERT OR REPLACE INTO instruments 
                    (symbol, name, category, market, currency, risk_level, min_investment, 
                     expense_ratio, dividend_yield, is_sharia_compliant, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    instrument.symbol, instrument.name, instrument.category, instrument.market,
                    instrument.currency, instrument.risk_level, instrument.min_investment,
                    instrument.expense_ratio, instrument.dividend_yield, instrument.is_sharia_compliant,
                    instrument.description
                ))
            except Exception as e:
                print(f"Error inserting {instrument.symbol}: {e}")
        
        self.conn.commit()
    
    def generate_historical_data(self, years: int = 5):
        """Generate realistic historical data for all instruments"""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years*365)
        
        # Get all instruments
        instruments = self.conn.execute('SELECT symbol, risk_level, market, category FROM instruments').fetchall()
        
        for symbol, risk_level, market, category in instruments:
            # Generate price series based on instrument characteristics
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
            
            # Base parameters for price generation
            initial_price = self._get_initial_price(category, market)
            annual_return = self._get_expected_return(risk_level, category, market)
            volatility = self._get_volatility(risk_level, category)
            
            # Generate price series using geometric Brownian motion
            prices = self._generate_price_series(initial_price, annual_return, volatility, len(dates))
            
            # Insert historical data
            for i, date in enumerate(dates):
                if i == 0:
                    open_price = high_price = low_price = close_price = prices[i]
                else:
                    close_price = prices[i]
                    open_price = prices[i-1]
                    # Add some realistic intraday variation
                    daily_range = abs(close_price - open_price) * random.uniform(1.2, 2.0)
                    high_price = max(open_price, close_price) + daily_range * 0.3
                    low_price = min(open_price, close_price) - daily_range * 0.3
                
                volume = random.randint(100000, 10000000) if category in ['ETF', 'Stock'] else None
                
                try:
                    self.conn.execute('''
                        INSERT OR IGNORE INTO historical_data 
                        (symbol, date, open_price, high_price, low_price, close_price, volume, adjusted_close)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        symbol, date.strftime('%Y-%m-%d'), 
                        round(open_price, 2), round(high_price, 2), 
                        round(low_price, 2), round(close_price, 2), 
                        volume, round(close_price, 2)
                    ))
                except Exception as e:
                    print(f"Error inserting historical data for {symbol}: {e}")
        
        self.conn.commit()
        self._calculate_performance_metrics()
    
    def _get_initial_price(self, category: str, market: str) -> float:
        """Get realistic initial price based on instrument type"""
        price_ranges = {
            'ETF': (50, 400),
            'Stock': (20, 200),
            'Bond': (95, 105),
            'Mutual Fund': (10, 50),
            'Commodity': (20, 2000),
            'Banking': (5, 15) if market == 'UAE' else (50, 200),
            'Real Estate': (2, 8) if market == 'UAE' else (50, 200),
        }
        
        range_vals = price_ranges.get(category, (10, 100))
        return random.uniform(range_vals[0], range_vals[1])
    
    def _get_expected_return(self, risk_level: int, category: str, market: str) -> float:
        """Get expected annual return based on risk level and type - Enhanced with realistic returns"""
        base_returns = {
            'UAE': {
                'Banking': 0.08, 'Real Estate': 0.06, 'Government Bond': 0.035, 'Islamic Bond': 0.04,
                'ETF': 0.07, 'Mutual Fund': 0.08, 'Islamic Fund': 0.075, 'Commodity': 0.05,
                'Telecommunications': 0.06, 'Utilities': 0.055, 'Energy': 0.07,
                'Transportation': 0.065, 'Infrastructure': 0.06, 'Financial Services': 0.075,
                'Healthcare': 0.07, 'Education': 0.065, 'Bond ETF': 0.04
            },
            'US': {
                'ETF': 0.10, 'Technology Stock': 0.15, 'Consumer Stock': 0.12, 'Automotive Stock': 0.18,
                'Bond ETF': 0.035, 'Mutual Fund': 0.09, 'REIT ETF': 0.08, 'Commodity ETF': 0.06,
                'Stock': 0.12
            }
        }

        # Get base return for the specific category
        market_returns = base_returns.get(market, {})
        base_return = market_returns.get(category, 0.08)

        # If category not found, try broader categories
        if base_return == 0.08 and category not in market_returns:
            if 'Stock' in category:
                base_return = market_returns.get('Stock', 0.12)
            elif 'Bond' in category:
                base_return = market_returns.get('Bond ETF', 0.035)
            elif 'ETF' in category:
                base_return = market_returns.get('ETF', 0.10)

        # Risk adjustment based on risk level
        risk_adjustment = (risk_level - 5) * 0.015  # Slightly higher adjustment

        # Market-specific adjustments
        if market == 'UAE':
            # UAE market typically has lower returns but more stability
            base_return *= 0.9

        return max(0.01, base_return + risk_adjustment)  # Ensure positive returns
    
    def _get_volatility(self, risk_level: int, category: str) -> float:
        """Get volatility based on risk level and category - Enhanced with realistic volatilities"""
        base_vol = 0.08 + (risk_level - 1) * 0.025  # Risk level 1-10 -> 0.08-0.305

        category_multipliers = {
            'Government Bond': 0.25, 'Islamic Bond': 0.3, 'Bond ETF': 0.35, 'Banking': 0.7,
            'ETF': 0.9, 'Mutual Fund': 0.85, 'Islamic Fund': 0.8, 'Stock': 1.1,
            'Technology Stock': 1.4, 'Consumer Stock': 1.2, 'Automotive Stock': 1.6,
            'Real Estate': 1.0, 'Commodity': 1.3, 'Commodity ETF': 1.2,
            'Telecommunications': 0.8, 'Utilities': 0.6, 'Energy': 1.1,
            'Transportation': 1.2, 'Infrastructure': 0.9, 'Financial Services': 1.0,
            'Healthcare': 0.9, 'Education': 0.8, 'REIT ETF': 1.0
        }

        # Get multiplier for specific category
        multiplier = category_multipliers.get(category, 1.0)

        # If category not found, try broader categories
        if multiplier == 1.0 and category not in category_multipliers:
            if 'Stock' in category:
                multiplier = 1.1
            elif 'Bond' in category:
                multiplier = 0.35
            elif 'ETF' in category:
                multiplier = 0.9

        return max(0.05, base_vol * multiplier)  # Minimum 5% volatility
    
    def _generate_price_series(self, initial_price: float, annual_return: float,
                              volatility: float, num_days: int) -> List[float]:
        """Generate realistic price series using enhanced geometric Brownian motion"""
        dt = 1/252  # Daily time step (252 trading days per year)
        prices = [initial_price]

        # Add market cycles and trends for more realism
        cycle_length = 252 * 2  # 2-year cycle
        trend_strength = 0.1

        for i in range(num_days - 1):
            # Base drift
            drift = annual_return * dt

            # Add cyclical component
            cycle_factor = np.sin(2 * np.pi * i / cycle_length) * trend_strength * dt

            # Add volatility clustering (GARCH-like effect)
            if i > 10:
                recent_volatility = np.std([prices[j] / prices[j-1] - 1 for j in range(max(0, i-10), i)])
                vol_adjustment = 1 + (recent_volatility - volatility) * 0.5
            else:
                vol_adjustment = 1

            # Random shock with adjusted volatility
            shock = volatility * vol_adjustment * np.sqrt(dt) * np.random.normal()

            # Price change calculation
            price_change = prices[-1] * (drift + cycle_factor + shock)
            new_price = max(prices[-1] + price_change, 0.01)  # Prevent negative prices

            # Add occasional jumps for more realism (rare events)
            if random.random() < 0.005:  # 0.5% chance of jump
                jump_size = random.uniform(-0.1, 0.1)  # ±10% jump
                new_price *= (1 + jump_size)

            prices.append(new_price)

        return prices
    
    def _calculate_performance_metrics(self):
        """Calculate performance metrics for all instruments"""
        
        instruments = self.conn.execute('SELECT DISTINCT symbol FROM instruments').fetchall()
        
        for (symbol,) in instruments:
            # Get historical data
            data = self.conn.execute('''
                SELECT date, close_price FROM historical_data 
                WHERE symbol = ? ORDER BY date
            ''', (symbol,)).fetchall()
            
            if len(data) < 252:  # Need at least 1 year of data
                continue
            
            dates = [row[0] for row in data]
            prices = [row[1] for row in data]
            
            # Calculate returns
            returns = [0] + [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
            
            # Calculate metrics
            ytd_return = self._calculate_ytd_return(dates, prices)
            one_year_return = (prices[-1] - prices[-252]) / prices[-252] if len(prices) >= 252 else None
            three_year_return = (prices[-1] - prices[-756]) / prices[-756] if len(prices) >= 756 else None
            five_year_return = (prices[-1] - prices[-1260]) / prices[-1260] if len(prices) >= 1260 else None
            
            volatility = np.std(returns) * np.sqrt(252)  # Annualized volatility
            sharpe_ratio = (np.mean(returns) * 252 - 0.02) / volatility if volatility > 0 else 0  # Assuming 2% risk-free rate
            max_drawdown = self._calculate_max_drawdown(prices)
            
            # Insert metrics
            self.conn.execute('''
                INSERT OR REPLACE INTO performance_metrics 
                (symbol, ytd_return, one_year_return, three_year_return, five_year_return, 
                 volatility, sharpe_ratio, max_drawdown)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol, ytd_return, one_year_return, three_year_return, five_year_return,
                volatility, sharpe_ratio, max_drawdown
            ))
        
        self.conn.commit()
    
    def _calculate_ytd_return(self, dates: List[str], prices: List[float]) -> float:
        """Calculate year-to-date return"""
        current_year = datetime.now().year
        year_start_idx = 0
        
        for i, date_str in enumerate(dates):
            if datetime.strptime(date_str, '%Y-%m-%d').year == current_year:
                year_start_idx = i
                break
        
        if year_start_idx < len(prices) - 1:
            return (prices[-1] - prices[year_start_idx]) / prices[year_start_idx]
        return 0
    
    def _calculate_max_drawdown(self, prices: List[float]) -> float:
        """Calculate maximum drawdown"""
        peak = prices[0]
        max_dd = 0
        
        for price in prices:
            if price > peak:
                peak = price
            drawdown = (peak - price) / peak
            max_dd = max(max_dd, drawdown)
        
        return max_dd
    
    # Database Query Methods
    def get_all_instruments(self) -> pd.DataFrame:
        """Get all investment instruments"""
        return pd.read_sql_query('SELECT * FROM instruments', self.conn)
    
    def get_instruments_by_market(self, market: str) -> pd.DataFrame:
        """Get instruments by market (UAE or US)"""
        return pd.read_sql_query('SELECT * FROM instruments WHERE market = ?', self.conn, params=(market,))
    
    def get_instruments_by_category(self, category: str) -> pd.DataFrame:
        """Get instruments by category"""
        return pd.read_sql_query('SELECT * FROM instruments WHERE category = ?', self.conn, params=(category,))
    
    def get_sharia_compliant_instruments(self) -> pd.DataFrame:
        """Get Sharia-compliant instruments"""
        return pd.read_sql_query('SELECT * FROM instruments WHERE is_sharia_compliant = 1', self.conn)
    
    def get_instruments_by_risk_level(self, min_risk: int, max_risk: int) -> pd.DataFrame:
        """Get instruments within risk range"""
        return pd.read_sql_query(
            'SELECT * FROM instruments WHERE risk_level BETWEEN ? AND ?', 
            self.conn, params=(min_risk, max_risk)
        )
    
    def get_historical_data(self, symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Get historical data for a specific instrument"""
        query = 'SELECT * FROM historical_data WHERE symbol = ?'
        params = [symbol]
        
        if start_date:
            query += ' AND date >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND date <= ?'
            params.append(end_date)
        
        query += ' ORDER BY date'
        return pd.read_sql_query(query, self.conn, params=params)
    
    def get_performance_metrics(self, symbol: str = None) -> pd.DataFrame:
        """Get performance metrics"""
        if symbol:
            return pd.read_sql_query('SELECT * FROM performance_metrics WHERE symbol = ?', self.conn, params=(symbol,))
        return pd.read_sql_query('SELECT * FROM performance_metrics', self.conn)
    
    def get_instrument_details(self, symbol: str) -> Dict:
        """Get detailed information about a specific instrument"""
        instrument = pd.read_sql_query('SELECT * FROM instruments WHERE symbol = ?', self.conn, params=(symbol,))
        performance = pd.read_sql_query('SELECT * FROM performance_metrics WHERE symbol = ?', self.conn, params=(symbol,))
        
        if instrument.empty:
            return None
        
        result = instrument.iloc[0].to_dict()
        if not performance.empty:
            result.update(performance.iloc[0].to_dict())
        
        return result
    
    def search_instruments(self, search_term: str) -> pd.DataFrame:
        """Search instruments by name or description"""
        query = '''
            SELECT * FROM instruments 
            WHERE name LIKE ? OR description LIKE ? OR symbol LIKE ?
        '''
        search_pattern = f'%{search_term}%'
        return pd.read_sql_query(query, self.conn, params=(search_pattern, search_pattern, search_pattern))
    
    def refresh_database(self, years: int = 7):
        """Refresh the database with new historical data and performance metrics"""
        print("🔄 Refreshing investment database...")

        # Clear existing historical data and performance metrics
        self.conn.execute('DELETE FROM historical_data')
        self.conn.execute('DELETE FROM performance_metrics')
        self.conn.commit()

        # Regenerate historical data with more years for better analysis
        self.generate_historical_data(years)

        print(f"✅ Database refreshed with {years} years of historical data")

        # Verify data quality
        self._verify_data_quality()

    def _verify_data_quality(self):
        """Verify that all instruments have sufficient data for analysis"""
        instruments = self.conn.execute('SELECT symbol FROM instruments').fetchall()

        insufficient_data = []
        for (symbol,) in instruments:
            data_count = self.conn.execute(
                'SELECT COUNT(*) FROM historical_data WHERE symbol = ?', (symbol,)
            ).fetchone()[0]

            if data_count < 1000:  # Less than ~4 years of data
                insufficient_data.append((symbol, data_count))

        if insufficient_data:
            print(f"⚠️  Warning: {len(insufficient_data)} instruments have insufficient data:")
            for symbol, count in insufficient_data[:5]:  # Show first 5
                print(f"   - {symbol}: {count} data points")
        else:
            print("✅ All instruments have sufficient historical data")

    def get_data_summary(self) -> Dict:
        """Get summary of database contents"""
        summary = {}

        # Count instruments by market
        uae_count = self.conn.execute("SELECT COUNT(*) FROM instruments WHERE market = 'UAE'").fetchone()[0]
        us_count = self.conn.execute("SELECT COUNT(*) FROM instruments WHERE market = 'US'").fetchone()[0]

        # Count Sharia-compliant instruments
        sharia_count = self.conn.execute("SELECT COUNT(*) FROM instruments WHERE is_sharia_compliant = 1").fetchone()[0]

        # Count historical data points
        total_data_points = self.conn.execute("SELECT COUNT(*) FROM historical_data").fetchone()[0]

        # Get date range
        date_range = self.conn.execute(
            "SELECT MIN(date), MAX(date) FROM historical_data"
        ).fetchone()

        summary = {
            'total_instruments': uae_count + us_count,
            'uae_instruments': uae_count,
            'us_instruments': us_count,
            'sharia_compliant': sharia_count,
            'total_data_points': total_data_points,
            'date_range': date_range,
            'avg_data_per_instrument': total_data_points / (uae_count + us_count) if (uae_count + us_count) > 0 else 0
        }

        return summary

    def close(self):
        """Close database connection"""
        self.conn.close()

# Example usage and testing functions
def demo_database():
    """Demonstrate database functionality"""
    print("Creating Investment Database...")
    db = InvestmentDatabase()
    
    print("\n=== All Instruments ===")
    instruments = db.get_all_instruments()
    print(f"Total instruments: {len(instruments)}")
    print(instruments[['symbol', 'name', 'market', 'category', 'risk_level']].head(10))
    
    print("\n=== UAE Market Instruments ===")
    uae_instruments = db.get_instruments_by_market('UAE')
    print(f"UAE instruments: {len(uae_instruments)}")
    print(uae_instruments[['symbol', 'name', 'category']].head())
    
    print("\n=== Sharia Compliant Instruments ===")
    sharia_instruments = db.get_sharia_compliant_instruments()
    print(f"Sharia compliant: {len(sharia_instruments)}")
    print(sharia_instruments[['symbol', 'name', 'market']].head())
    
    print("\n=== Historical Data Sample (SPY) ===")
    spy_data = db.get_historical_data('SPY')
    if not spy_data.empty:
        print(f"SPY data points: {len(spy_data)}")
        print(spy_data.tail())
    
    print("\n=== Performance Metrics Sample ===")
    performance = db.get_performance_metrics()
    print(performance.head())
    
    print("\n=== Search Example (Gold) ===")
    gold_instruments = db.search_instruments('gold')
    print(gold_instruments[['symbol', 'name', 'description']])
    
    db.close()
    print("\nDatabase demo completed!")

if __name__ == "__main__":
    demo_database()
