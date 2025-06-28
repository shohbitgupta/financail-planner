
import os
import sys
from pathlib import Path
from flask import Flask, send_from_directory, send_file, jsonify, request
from flask_cors import CORS
import json

# Add current directory to path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import the existing Flask API
try:
    from flask_api.standalone_app import app as api_app, generate_financial_plan_logic
    print("✅ Successfully imported Flask API")
    HAS_FULL_API = True
except ImportError as e:
    print(f"⚠️ Failed to import Flask API: {e}")
    # Create a basic Flask app as fallback
    api_app = Flask(__name__)
    CORS(api_app)
    HAS_FULL_API = False

# Configure the app for production
api_app.config['ENV'] = 'production'
api_app.config['DEBUG'] = False

# Enable CORS for all routes
CORS(api_app, origins=['*'])

# Add health check endpoint
@api_app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'Financial Planner AI Agent',
        'version': '1.0.0',
        'features': {
            'full_api': HAS_FULL_API,
            'react_ui': True,
            'ai_integration': HAS_FULL_API
        }
    })

# Add financial plan endpoint if not already present
if HAS_FULL_API:
    print("✅ Using full API with AI integration")
else:
    @api_app.route('/api/generate-financial-plan', methods=['POST'])
    def generate_plan_fallback():
        """Fallback financial plan generation"""
        try:
            user_data = request.get_json()
            # Simple fallback response
            return jsonify({
                'monthly_savings_needed': 2500,
                'total_investment_needed': 500000,
                'goal_achievement_timeline': {
                    'retirement': {'years': 25, 'achievable': True}
                },
                'recommendations': [{
                    'symbol': 'SPY',
                    'name': 'SPDR S&P 500 ETF',
                    'category': 'Equity',
                    'allocation_percentage': 60,
                    'platform_recommendation': {
                        'platform_name': 'WIO Bank',
                        'app_name': 'WIO Invest App'
                    }
                }]
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# Serve React build files
@api_app.route('/')
def serve_react_app():
    """Serve the React app"""
    build_dir = current_dir / 'react_financial_ui' / 'build'
    if build_dir.exists():
        return send_file(build_dir / 'index.html')
    else:
        return '<h1>Financial Planner AI Agent</h1><p>Building React app... Please wait and refresh.</p>'

@api_app.route('/<path:path>')
def serve_react_static(path):
    """Serve React static files"""
    build_dir = current_dir / 'react_financial_ui' / 'build'
    if build_dir.exists() and (build_dir / path).exists():
        return send_from_directory(build_dir, path)
    else:
        # Fallback to index.html for SPA routing
        if build_dir.exists():
            return send_file(build_dir / 'index.html')
        else:
            return '<h1>Financial Planner AI Agent</h1><p>React build not found.</p>'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f"🚀 Starting Financial Planner AI Agent on port {port}")
    print(f"🌐 Access your app at: https://your-repl-name.your-username.repl.co")
    api_app.run(host='0.0.0.0', port=port, debug=False)
