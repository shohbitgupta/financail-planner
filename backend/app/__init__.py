"""
Flask application factory for Financial Planner AI.
"""
from flask import Flask
from flask_cors import CORS
import logging
from backend.config import config

def create_app(config_name='default'):
    """Create and configure Flask application."""
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, app.config['LOG_LEVEL']),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize databases
    _initialize_databases(app)

    # Initialize services
    _initialize_services(app)

    # Register blueprints
    from app.api import financial_planning_bp, health_bp

    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(financial_planning_bp, url_prefix=app.config['API_PREFIX'])
    
    @app.route('/')
    def index():
        return {
            'message': 'Financial Planner AI Backend',
            'version': app.config['API_VERSION'],
            'status': 'running'
        }
    
    app.logger.info(f"Financial Planner AI Backend started in {config_name} mode")

    return app

def _initialize_databases(app):
    """Initialize database connections."""
    with app.app_context():
        # Initialize investment database
        from app.database.investment_db import initialize_investment_db
        investment_db_path = app.config['DATABASE_DIR'] / 'investment_database.db'
        initialize_investment_db(investment_db_path)

        # Initialize vector database
        from app.database.vector_db import initialize_vector_db
        vector_db_path = app.config['VECTOR_DB_PATH']
        collection_name = app.config['VECTOR_COLLECTION_NAME']
        embedding_model = app.config['EMBEDDING_MODEL']
        initialize_vector_db(vector_db_path, collection_name, embedding_model)

        app.logger.info("Databases initialized successfully")

def _initialize_services(app):
    """Initialize business logic services."""
    with app.app_context():
        from app.services import initialize_services
        initialize_services(app)
