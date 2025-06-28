"""
Health check API endpoints.
"""
from flask import Blueprint, jsonify, current_app
from app.services import llm_service, vector_service

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Financial Planner AI Backend',
        'version': current_app.config['API_VERSION']
    })

@health_bp.route('/health/detailed', methods=['GET'])
def detailed_health_check():
    """Detailed health check including service dependencies."""
    
    health_status = {
        'status': 'healthy',
        'service': 'Financial Planner AI Backend',
        'version': current_app.config['API_VERSION'],
        'components': {}
    }
    
    # Check Ollama LLM service
    try:
        ollama_status = llm_service.check_health()
        health_status['components']['ollama'] = {
            'status': 'healthy' if ollama_status else 'unhealthy',
            'model': current_app.config['OLLAMA_MODEL']
        }
    except Exception as e:
        health_status['components']['ollama'] = {
            'status': 'error',
            'error': str(e)
        }
    
    # Check Vector Database
    try:
        vector_status = vector_service.check_health()
        health_status['components']['vector_db'] = {
            'status': 'healthy' if vector_status else 'unhealthy',
            'collection': current_app.config['VECTOR_COLLECTION_NAME']
        }
    except Exception as e:
        health_status['components']['vector_db'] = {
            'status': 'error',
            'error': str(e)
        }
    
    # Check Investment Database
    try:
        from app.database import investment_db
        db_status = investment_db.check_health()
        health_status['components']['investment_db'] = {
            'status': 'healthy' if db_status else 'unhealthy'
        }
    except Exception as e:
        health_status['components']['investment_db'] = {
            'status': 'error',
            'error': str(e)
        }
    
    # Overall status
    component_statuses = [comp['status'] for comp in health_status['components'].values()]
    if 'error' in component_statuses or 'unhealthy' in component_statuses:
        health_status['status'] = 'degraded'
    
    return jsonify(health_status)
