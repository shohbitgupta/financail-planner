"""
Investment database access layer.
"""
import sqlite3
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from app.models.investment import Investment, InvestmentMetrics

logger = logging.getLogger(__name__)

class InvestmentDatabase:
    """Database access for investment data."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database tables if they don't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create investments table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS investments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        category TEXT NOT NULL,
                        subcategory TEXT,
                        market TEXT NOT NULL,
                        exchange TEXT,
                        currency TEXT DEFAULT 'AED',
                        expected_return REAL DEFAULT 0.0,
                        risk_level INTEGER DEFAULT 5,
                        is_sharia_compliant BOOLEAN DEFAULT 0,
                        is_esg_compliant BOOLEAN DEFAULT 0,
                        min_investment REAL,
                        max_investment REAL,
                        description TEXT,
                        issuer TEXT,
                        sector TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create investment_metrics table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS investment_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        investment_id INTEGER NOT NULL,
                        ytd_return REAL,
                        one_year_return REAL,
                        three_year_return REAL,
                        five_year_return REAL,
                        ten_year_return REAL,
                        volatility REAL,
                        sharpe_ratio REAL,
                        max_drawdown REAL,
                        beta REAL,
                        dividend_yield REAL,
                        distribution_frequency TEXT,
                        expense_ratio REAL,
                        management_fee REAL,
                        assets_under_management REAL,
                        inception_date DATE,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (investment_id) REFERENCES investments (id)
                    )
                ''')
                
                conn.commit()
                logger.info("Investment database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing investment database: {str(e)}")
            raise
    
    def get_all_investments(self) -> List[Investment]:
        """Get all investments from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT i.*, m.* FROM investments i
                    LEFT JOIN investment_metrics m ON i.id = m.investment_id
                ''')
                
                rows = cursor.fetchall()
                investments = []
                
                for row in rows:
                    # Create metrics object
                    metrics = None
                    if row['ytd_return'] is not None:
                        metrics = InvestmentMetrics(
                            ytd_return=row['ytd_return'],
                            one_year_return=row['one_year_return'],
                            three_year_return=row['three_year_return'],
                            five_year_return=row['five_year_return'],
                            ten_year_return=row['ten_year_return'],
                            volatility=row['volatility'],
                            sharpe_ratio=row['sharpe_ratio'],
                            max_drawdown=row['max_drawdown'],
                            beta=row['beta'],
                            dividend_yield=row['dividend_yield'],
                            distribution_frequency=row['distribution_frequency'],
                            expense_ratio=row['expense_ratio'],
                            management_fee=row['management_fee'],
                            assets_under_management=row['assets_under_management']
                        )
                    
                    # Create investment object
                    investment = Investment(
                        symbol=row['symbol'],
                        name=row['name'],
                        category=row['category'],
                        subcategory=row['subcategory'],
                        market=row['market'],
                        exchange=row['exchange'],
                        currency=row['currency'],
                        expected_return=row['expected_return'],
                        risk_level=row['risk_level'],
                        is_sharia_compliant=bool(row['is_sharia_compliant']),
                        is_esg_compliant=bool(row['is_esg_compliant']),
                        min_investment=row['min_investment'],
                        max_investment=row['max_investment'],
                        description=row['description'],
                        issuer=row['issuer'],
                        sector=row['sector'],
                        metrics=metrics
                    )
                    
                    investments.append(investment)
                
                logger.info(f"Retrieved {len(investments)} investments from database")
                return investments
                
        except Exception as e:
            logger.error(f"Error retrieving investments: {str(e)}")
            return []
    
    def get_investments_by_criteria(self, criteria: Dict[str, Any]) -> List[Investment]:
        """Get investments matching specific criteria."""
        try:
            all_investments = self.get_all_investments()
            
            # Filter investments based on criteria
            filtered_investments = []
            for investment in all_investments:
                if investment.matches_criteria(criteria):
                    filtered_investments.append(investment)
            
            logger.info(f"Found {len(filtered_investments)} investments matching criteria")
            return filtered_investments
            
        except Exception as e:
            logger.error(f"Error filtering investments: {str(e)}")
            return []
    
    def get_investment_by_symbol(self, symbol: str) -> Optional[Investment]:
        """Get investment by symbol."""
        try:
            investments = self.get_all_investments()
            for investment in investments:
                if investment.symbol == symbol:
                    return investment
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving investment {symbol}: {str(e)}")
            return None
    
    def add_investment(self, investment: Investment) -> bool:
        """Add new investment to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Insert investment
                cursor.execute('''
                    INSERT INTO investments (
                        symbol, name, category, subcategory, market, exchange, currency,
                        expected_return, risk_level, is_sharia_compliant, is_esg_compliant,
                        min_investment, max_investment, description, issuer, sector
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    investment.symbol, investment.name, investment.category, investment.subcategory,
                    investment.market, investment.exchange, investment.currency,
                    investment.expected_return, investment.risk_level,
                    investment.is_sharia_compliant, investment.is_esg_compliant,
                    investment.min_investment, investment.max_investment,
                    investment.description, investment.issuer, investment.sector
                ))
                
                investment_id = cursor.lastrowid
                
                # Insert metrics if available
                if investment.metrics:
                    cursor.execute('''
                        INSERT INTO investment_metrics (
                            investment_id, ytd_return, one_year_return, three_year_return,
                            five_year_return, ten_year_return, volatility, sharpe_ratio,
                            max_drawdown, beta, dividend_yield, distribution_frequency,
                            expense_ratio, management_fee, assets_under_management
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        investment_id, investment.metrics.ytd_return,
                        investment.metrics.one_year_return, investment.metrics.three_year_return,
                        investment.metrics.five_year_return, investment.metrics.ten_year_return,
                        investment.metrics.volatility, investment.metrics.sharpe_ratio,
                        investment.metrics.max_drawdown, investment.metrics.beta,
                        investment.metrics.dividend_yield, investment.metrics.distribution_frequency,
                        investment.metrics.expense_ratio, investment.metrics.management_fee,
                        investment.metrics.assets_under_management
                    ))
                
                conn.commit()
                logger.info(f"Added investment: {investment.symbol}")
                return True
                
        except Exception as e:
            logger.error(f"Error adding investment {investment.symbol}: {str(e)}")
            return False
    
    def update_investment(self, investment: Investment) -> bool:
        """Update existing investment in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Update investment
                cursor.execute('''
                    UPDATE investments SET
                        name=?, category=?, subcategory=?, market=?, exchange=?, currency=?,
                        expected_return=?, risk_level=?, is_sharia_compliant=?, is_esg_compliant=?,
                        min_investment=?, max_investment=?, description=?, issuer=?, sector=?,
                        updated_at=CURRENT_TIMESTAMP
                    WHERE symbol=?
                ''', (
                    investment.name, investment.category, investment.subcategory,
                    investment.market, investment.exchange, investment.currency,
                    investment.expected_return, investment.risk_level,
                    investment.is_sharia_compliant, investment.is_esg_compliant,
                    investment.min_investment, investment.max_investment,
                    investment.description, investment.issuer, investment.sector,
                    investment.symbol
                ))
                
                conn.commit()
                logger.info(f"Updated investment: {investment.symbol}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating investment {investment.symbol}: {str(e)}")
            return False
    
    def delete_investment(self, symbol: str) -> bool:
        """Delete investment from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get investment ID
                cursor.execute('SELECT id FROM investments WHERE symbol=?', (symbol,))
                row = cursor.fetchone()
                
                if row:
                    investment_id = row[0]
                    
                    # Delete metrics first
                    cursor.execute('DELETE FROM investment_metrics WHERE investment_id=?', (investment_id,))
                    
                    # Delete investment
                    cursor.execute('DELETE FROM investments WHERE id=?', (investment_id,))
                    
                    conn.commit()
                    logger.info(f"Deleted investment: {symbol}")
                    return True
                else:
                    logger.warning(f"Investment not found: {symbol}")
                    return False
                
        except Exception as e:
            logger.error(f"Error deleting investment {symbol}: {str(e)}")
            return False
    
    def check_health(self) -> bool:
        """Check if database is accessible."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM investments')
                cursor.fetchone()
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False

# Global database instance - will be initialized by config
investment_db = None

def initialize_investment_db(db_path: Path):
    """Initialize global investment database instance."""
    global investment_db
    investment_db = InvestmentDatabase(db_path)
    return investment_db
