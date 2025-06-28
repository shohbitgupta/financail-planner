"""
Configuration settings for the Financial Planner AI application.
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # API settings
    API_VERSION = 'v1'
    API_PREFIX = f'/api/{API_VERSION}'
    
    # Database settings
    DATABASE_DIR = BASE_DIR / 'data' / 'databases'
    INVESTMENT_DB_PATH = DATABASE_DIR / 'investment.db'
    VECTOR_DB_PATH = DATABASE_DIR / 'vector_db'
    
    # Historical data
    HISTORICAL_DATA_DIR = BASE_DIR / 'data' / 'historical'
    ADX_DATA_PATH = HISTORICAL_DATA_DIR / 'adx_data.csv'
    DFM_DATA_PATH = HISTORICAL_DATA_DIR / 'dfm_data.csv'
    
    # LLM settings
    OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama3.2')
    OLLAMA_BASE_URL = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
    
    # Gemini settings (for evaluator)
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.0-flash-exp')
    
    # Vector database settings
    VECTOR_COLLECTION_NAME = 'enhanced_investment_data'
    EMBEDDING_MODEL = 'mxbai-embed-large'
    VECTOR_SEARCH_K = 10
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    @classmethod
    def init_app(cls, app):
        """Initialize application with configuration."""
        # Ensure directories exist
        cls.DATABASE_DIR.mkdir(parents=True, exist_ok=True)
        cls.HISTORICAL_DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
