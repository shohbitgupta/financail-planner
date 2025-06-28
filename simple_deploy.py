#!/usr/bin/env python3
"""
Simple deployment script for Financial Planner AI Agent
This creates a unified Flask app that serves both API and React build
"""

import os
import sys
from pathlib import Path
from flask import Flask, send_from_directory, send_file, jsonify
from flask_cors import CORS

# Add current directory to path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / 'flask_api'))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Create Flask app
app = Flask(__name__)
CORS(app, origins=['*'])

# Configure the app
app.config['ENV'] = 'production'
app.config['DEBUG'] = False

# Try to import the existing API routes
try:
    from flask_api.standalone_app import generate_financial_plan
    print("✅ Successfully imported financial plan API")
    
    # Register the API route
    app.add_url_rule('/api/generate-financial-plan', 'generate_financial_plan', 
                     generate_financial_plan, methods=['POST'])
    HAS_FULL_API = True
except ImportError as e:
    print(f"⚠️ Failed to import full API: {e}")
    HAS_FULL_API = False

# Health check endpoint
@app.route('/api/health')
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

# Fallback API endpoint if full API not available
if not HAS_FULL_API:
    @app.route('/api/generate-financial-plan', methods=['POST'])
    def generate_plan_fallback():
        """Fallback financial plan generation"""
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

# Serve React build files
@app.route('/')
def serve_react_app():
    """Serve the React app"""
    build_dir = current_dir / 'react_financial_ui' / 'build'
    if build_dir.exists():
        return send_file(build_dir / 'index.html')
    else:
        return '<h1>Financial Planner AI Agent</h1><p>React build not found. Please run: cd react_financial_ui && npm run build</p>'

@app.route('/<path:path>')
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
    print(f"🌐 Local access: http://localhost:{port}")
    print(f"🌐 Network access: http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
