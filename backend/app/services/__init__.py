"""
Business logic services for Financial Planner AI.
"""
from . import financial_service
from . import portfolio_service
from . import llm_service
from . import evaluator_service
from . import vector_service

def initialize_services(app):
    """Initialize all services with Flask app context."""
    
    with app.app_context():
        # Initialize vector service
        vector_service.initialize(
            db_path=app.config['VECTOR_DB_PATH'],
            collection_name=app.config['VECTOR_COLLECTION_NAME'],
            embedding_model=app.config['EMBEDDING_MODEL']
        )
        
        # Initialize LLM service
        llm_service.initialize(
            model_name=app.config['OLLAMA_MODEL'],
            base_url=app.config['OLLAMA_BASE_URL']
        )
        
        # Initialize evaluator service
        if app.config.get('GEMINI_API_KEY'):
            evaluator_service.initialize(
                api_key=app.config['GEMINI_API_KEY'],
                model_name=app.config['GEMINI_MODEL']
            )
        
        app.logger.info("All services initialized successfully")

__all__ = [
    'financial_service',
    'portfolio_service', 
    'llm_service',
    'evaluator_service',
    'vector_service',
    'initialize_services'
]
