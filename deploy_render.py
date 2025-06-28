#!/usr/bin/env python3
"""
Render.com deployment script for Financial Planner AI Agent
This script prepares the application for Render deployment
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_render_deployment():
    """Setup the application for Render deployment"""
    print("🚀 Setting up Financial Planner AI Agent for Render deployment...")
    
    # Update simple_deploy.py for Render
    render_port = os.environ.get('PORT', '10000')
    
    # Create Render-optimized deployment script
    render_app_content = f'''#!/usr/bin/env python3
"""
Render.com optimized deployment for Financial Planner AI Agent
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

# Configure the app for Render
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
    print(f"⚠️ Failed to import full API: {{e}}")
    HAS_FULL_API = False

# Health check endpoint
@app.route('/api/health')
def health():
    return jsonify({{
        'status': 'healthy',
        'service': 'Financial Planner AI Agent',
        'version': '1.0.0',
        'platform': 'Render',
        'features': {{
            'full_api': HAS_FULL_API,
            'react_ui': True,
            'ai_integration': HAS_FULL_API
        }}
    }})

# Fallback API endpoint if full API not available
if not HAS_FULL_API:
    @app.route('/api/generate-financial-plan', methods=['POST'])
    def generate_plan_fallback():
        """Fallback financial plan generation"""
        return jsonify({{
            'monthly_savings_needed': 2500,
            'total_investment_needed': 500000,
            'goal_achievement_timeline': {{
                'retirement': {{'years': 25, 'achievable': True}}
            }},
            'recommendations': [{{
                'symbol': 'SPY',
                'name': 'SPDR S&P 500 ETF',
                'category': 'Equity',
                'allocation_percentage': 60,
                'platform_recommendation': {{
                    'platform_name': 'WIO Bank',
                    'app_name': 'WIO Invest App'
                }}
            }}]
        }})

# Serve React build files
@app.route('/')
def serve_react_app():
    """Serve the React app"""
    build_dir = current_dir / 'react_financial_ui' / 'build'
    if build_dir.exists():
        return send_file(build_dir / 'index.html')
    else:
        return '<h1>Financial Planner AI Agent</h1><p>Building React app...</p>'

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
    port = int(os.environ.get('PORT', {render_port}))
    print(f"🚀 Starting Financial Planner AI Agent on Render")
    print(f"🌐 Port: {{port}}")
    app.run(host='0.0.0.0', port=port, debug=False)
'''
    
    # Write the Render-optimized app
    with open('render_app.py', 'w') as f:
        f.write(render_app_content)
    
    print("✅ Created render_app.py")
    
    # Create requirements.txt optimized for Render
    render_requirements = """Flask==2.3.3
Flask-CORS==4.0.0
python-dotenv==1.0.0
requests==2.31.0
langchain
langchain-ollama
chromadb
sqlite3
google-generativeai
"""
    
    with open('requirements_render.txt', 'w') as f:
        f.write(render_requirements)
    
    print("✅ Created requirements_render.txt")
    
    print("\n🎯 Next Steps for Render Deployment:")
    print("1. Push your code to GitHub")
    print("2. Go to https://render.com")
    print("3. Connect your GitHub repository")
    print("4. Choose 'Web Service'")
    print("5. Set these configurations:")
    print("   - Build Command: pip install -r requirements_render.txt && cd react_financial_ui && npm install && npm run build")
    print("   - Start Command: python render_app.py")
    print("   - Add Environment Variable: GEMINI_API_KEY")
    print("6. Deploy!")
    print("\n🌐 Your app will be live at: https://your-app-name.onrender.com")

if __name__ == "__main__":
    setup_render_deployment()
