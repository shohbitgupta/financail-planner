"""
Financial planning API endpoints.
"""
from flask import Blueprint, request, jsonify
from backend.app.models.user_profile import UserProfile
from backend.app.services import financial_service
from backend.app.utils.validators import validate_user_input
import logging

logger = logging.getLogger(__name__)

financial_planning_bp = Blueprint('financial_planning', __name__)

@financial_planning_bp.route('/generate-financial-plan', methods=['POST'])
def generate_financial_plan():
    """Generate a comprehensive financial plan based on user input."""
    
    try:
        # Get and validate user input
        user_data = request.get_json()
        if not user_data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate input data
        validation_result = validate_user_input(user_data)
        if not validation_result['valid']:
            return jsonify({
                'error': 'Invalid input data',
                'details': validation_result['errors']
            }), 400
        
        # Create user profile
        user_profile = UserProfile.from_dict(user_data)
        
        logger.info(f"Generating financial plan for user: age={user_profile.age}, "
                   f"risk_tolerance={user_profile.risk_tolerance}, "
                   f"market={user_profile.preferred_market}")
        
        # Generate financial plan
        financial_plan = financial_service.generate_comprehensive_plan(user_profile)
        
        logger.info("Financial plan generated successfully")
        
        return jsonify(financial_plan)
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({'error': f'Validation error: {str(e)}'}), 400
        
    except Exception as e:
        logger.error(f"Error generating financial plan: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@financial_planning_bp.route('/portfolio-recommendations', methods=['POST'])
def get_portfolio_recommendations():
    """Get portfolio recommendations based on user profile."""
    
    try:
        user_data = request.get_json()
        if not user_data:
            return jsonify({'error': 'No data provided'}), 400
        
        user_profile = UserProfile.from_dict(user_data)
        
        # Get portfolio recommendations
        recommendations = financial_service.get_portfolio_recommendations(user_profile)
        
        return jsonify({
            'recommendations': recommendations,
            'user_profile': user_profile.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error getting portfolio recommendations: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@financial_planning_bp.route('/risk-assessment', methods=['POST'])
def assess_risk():
    """Assess user risk profile."""
    
    try:
        user_data = request.get_json()
        if not user_data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Perform risk assessment
        risk_assessment = financial_service.assess_risk_profile(user_data)
        
        return jsonify(risk_assessment)
        
    except Exception as e:
        logger.error(f"Error assessing risk: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
