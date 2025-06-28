#!/usr/bin/env python3
"""
Replit Deployment Script for Financial Planner AI Agent
Handles both React frontend and Flask backend deployment
"""

import os
import sys
import subprocess
import threading
import time
import signal
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

def setup_environment():
    """Setup environment variables for Replit"""
    os.environ['PYTHONPATH'] = str(current_dir)
    os.environ['FLASK_ENV'] = 'production'
    os.environ['PORT'] = '3000'
    
    # Create .env file if it doesn't exist
    env_file = current_dir / '.env'
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write("# Financial Planner AI Agent Environment Variables\n")
            f.write("GEMINI_API_KEY=your_gemini_api_key_here\n")
            f.write("OLLAMA_HOST=localhost:11434\n")
            f.write("OLLAMA_MODEL=llama3.2\n")
        print("📝 Created .env file - please add your API keys")

def install_dependencies():
    """Install Python and Node.js dependencies"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "flask_api/requirements.txt"
        ])
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "chromadb"
        ])
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Python dependency installation failed: {e}")
    
    print("📦 Installing Node.js dependencies...")
    try:
        os.chdir("react_financial_ui")
        subprocess.check_call(["npm", "install"])
        print("🔨 Building React application...")
        subprocess.check_call(["npm", "run", "build"])
        os.chdir("..")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Node.js dependency installation failed: {e}")
        os.chdir("..")

def setup_ollama():
    """Setup Ollama if possible (optional for Replit)"""
    try:
        print("🤖 Attempting to setup Ollama...")
        # Check if Ollama is available
        result = subprocess.run(["which", "ollama"], capture_output=True)
        if result.returncode != 0:
            print("⚠️ Ollama not available - using fallback mode")
            return False
        
        # Pull the model
        subprocess.check_call(["ollama", "pull", "llama3.2"])
        print("✅ Ollama setup complete")
        return True
    except Exception as e:
        print(f"⚠️ Ollama setup failed: {e}")
        return False

def create_unified_app():
    """Create a unified Flask app that serves both API and React build"""
    app_content = '''
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
'''

    with open('replit_app.py', 'w') as f:
        f.write(app_content)

def main():
    """Main deployment function"""
    print("🚀 Financial Planner AI Agent - Replit Deployment")
    print("=" * 50)
    
    # Setup environment
    setup_environment()
    
    # Install dependencies
    install_dependencies()
    
    # Setup Ollama (optional)
    setup_ollama()
    
    # Create unified app
    create_unified_app()
    
    print("\n✅ Deployment setup complete!")
    print("🌐 Starting the application...")
    
    # Start the unified app
    try:
        print("🚀 Starting the unified Flask application...")
        exec(open('replit_app.py').read())
    except Exception as e:
        print(f"⚠️ Failed to start unified app: {e}")
        print("Starting basic HTTP server as fallback...")
        os.system("python -m http.server 3000")

if __name__ == "__main__":
    main()
