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
from flask import Flask, send_from_directory, send_file
from flask_cors import CORS

# Add current directory to path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# Import the existing Flask API
try:
    from flask_api.standalone_app import app as api_app
    print("✅ Successfully imported Flask API")
except ImportError as e:
    print(f"⚠️ Failed to import Flask API: {e}")
    # Create a basic Flask app as fallback
    api_app = Flask(__name__)
    CORS(api_app)
    
    @api_app.route('/api/health')
    def health():
        return {'status': 'ok', 'message': 'API is running'}

# Configure the app for production
api_app.config['ENV'] = 'production'
api_app.config['DEBUG'] = False

# Serve React build files
@api_app.route('/')
def serve_react_app():
    """Serve the React app"""
    build_dir = current_dir / 'react_financial_ui' / 'build'
    if build_dir.exists():
        return send_file(build_dir / 'index.html')
    else:
        return '<h1>Financial Planner AI Agent</h1><p>React build not found. Please run: cd react_financial_ui && npm run build</p>'

@api_app.route('/<path:path>')
def serve_react_static(path):
    """Serve React static files"""
    build_dir = current_dir / 'react_financial_ui' / 'build'
    if build_dir.exists():
        return send_from_directory(build_dir, path)
    else:
        return send_file(build_dir / 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f"🚀 Starting Financial Planner AI Agent on port {port}")
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
        import replit_app
    except ImportError:
        print("⚠️ Failed to import unified app, starting basic server...")
        os.system("python -m http.server 3000")

if __name__ == "__main__":
    main()
