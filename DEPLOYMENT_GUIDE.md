# 🚀 Financial Planner AI Agent - Deployment Guide

This guide provides comprehensive instructions for deploying the Financial Planner AI Agent on **Replit** and **Vercel**.

## 📋 Architecture Overview

- **Frontend**: React TypeScript application with Tailwind CSS
- **Backend**: Flask API with Ollama integration and vector database
- **Database**: SQLite + ChromaDB vector database
- **AI Models**: Ollama 3.2 (local) + Gemini 2.5 Pro (evaluator)

## 🔧 Prerequisites

Before deployment, ensure you have:

- Environment variables configured (`.env` file)
- Gemini API key for evaluator agent
- All dependencies listed in requirements files

---

## 🌐 Option 1: Replit Deployment (Full-Stack)

Replit is ideal for this project as it supports both Python backend and Node.js frontend in a single environment.

### Step 1: Create Replit Project

1. Go to [replit.com](https://replit.com) and create a new Repl
2. Choose **"Python"** as the template
3. Name your project: `financial-planner-ai-agent`

### Step 2: Upload Project Files

Upload all project files to Replit:

```bash
# Main project structure
├── flask_api/          # Backend API
├── react_financial_ui/ # Frontend React app
├── enhanced_investment_vector_db/ # Vector database
├── *.py               # Python modules
├── *.csv              # Historical data
└── requirements.txt   # Python dependencies
```

### Step 3: Configure Replit Environment

Create `.replit` configuration file:

```toml
# .replit
run = "python deploy_replit.py"
language = "python3"

[nix]
channel = "stable-22_11"

[deployment]
run = ["sh", "-c", "python deploy_replit.py"]
```

### Step 4: Install Dependencies

Create `replit_setup.py`:

```python
import subprocess
import sys
import os

def install_python_deps():
    """Install Python dependencies"""
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "flask_api/requirements.txt"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "chromadb", "sqlite3"])

def install_node_deps():
    """Install Node.js dependencies"""
    os.chdir("react_financial_ui")
    subprocess.check_call(["npm", "install"])
    subprocess.check_call(["npm", "run", "build"])
    os.chdir("..")

def setup_ollama():
    """Setup Ollama (if available)"""
    try:
        subprocess.check_call(["curl", "-fsSL", "https://ollama.ai/install.sh", "|", "sh"])
        subprocess.check_call(["ollama", "pull", "llama3.2"])
    except:
        print("⚠️ Ollama setup failed - will use fallback mode")

if __name__ == "__main__":
    print("🔧 Setting up Financial Planner AI Agent...")
    install_python_deps()
    install_node_deps()
    setup_ollama()
    print("✅ Setup complete!")
```

### Step 5: Create Deployment Script

Create `deploy_replit.py`:

```python
import os
import subprocess
import threading
import time
from flask_api.standalone_app import app

def start_react_build():
    """Serve React build files"""
    os.chdir("react_financial_ui")
    if not os.path.exists("build"):
        subprocess.run(["npm", "run", "build"])

    # Serve static files through Flask
    return True

def main():
    print("🚀 Starting Financial Planner AI Agent...")

    # Set environment variables
    os.environ['FLASK_ENV'] = 'production'
    os.environ['PORT'] = '3000'

    # Build React app
    start_react_build()

    # Start Flask app (serves both API and React build)
    app.run(host='0.0.0.0', port=3000, debug=False)

if __name__ == "__main__":
    main()
```

---

## ☁️ Option 2: Vercel Deployment (Recommended)

Vercel provides excellent support for full-stack applications with serverless functions.

### Step 1: Prepare for Vercel

Create `vercel.json` configuration:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "react_financial_ui/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "build"
      }
    },
    {
      "src": "api/*.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/react_financial_ui/$1"
    }
  ],
  "env": {
    "GEMINI_API_KEY": "@gemini_api_key"
  }
}
```

### Step 2: Create API Directory

Create `api/` directory for Vercel serverless functions:

```bash
mkdir api
```

### Step 3: Convert Flask Routes to Vercel Functions

Create `api/generate-financial-plan.py`:

```python
from flask import Flask, request, jsonify
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask_api.standalone_app import generate_financial_plan_logic

app = Flask(__name__)

def handler(request):
    if request.method == 'POST':
        try:
            user_data = request.get_json()
            result = generate_financial_plan_logic(user_data)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Method not allowed'}), 405
```

### Step 4: Update React Build Configuration

Update `react_financial_ui/package.json`:

```json
{
  "scripts": {
    "build": "react-scripts build && cp -r build/* ../public/"
  }
}
```

### Step 5: Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

---

## 🔐 Environment Variables Setup

For both platforms, configure these environment variables:

```bash
# Required for Gemini evaluator
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Ollama configuration
OLLAMA_HOST=localhost:11434
OLLAMA_MODEL=llama3.2

# Database paths (auto-configured)
VECTOR_DB_PATH=./enhanced_investment_vector_db
INVESTMENT_DB_PATH=./flask_api/investment_database.db
```

---

## 🎯 Platform-Specific Considerations

### Replit Advantages:

- ✅ Full Python + Node.js environment
- ✅ Built-in terminal and file management
- ✅ Can run Ollama locally
- ✅ Persistent storage
- ✅ Real-time collaboration

### Vercel Advantages:

- ✅ Serverless architecture (better scaling)
- ✅ Global CDN for React app
- ✅ Automatic HTTPS
- ✅ Git integration
- ✅ Professional deployment pipeline

### Limitations:

- **Replit**: Limited computational resources for AI models
- **Vercel**: Serverless functions have execution time limits (10s for hobby plan)

---

## 🚀 Quick Start Commands

### For Replit:

```bash
# 1. Upload files to Replit
# 2. Run setup
python replit_setup.py

# 3. Start application
python deploy_replit.py
```

### For Vercel:

```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Build React app
cd react_financial_ui && npm run build

# 3. Deploy
vercel --prod
```

---

## 📊 Expected Results

After successful deployment:

- **Frontend**: Accessible via provided URL
- **API Endpoints**: `/api/generate-financial-plan`
- **Features**: Full financial planning with WIO Bank integration
- **Performance**: Real-time AI-powered recommendations

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Replit Issues:

1. **Python Import Errors**

   ```bash
   # Solution: Add to Python path
   export PYTHONPATH="/home/runner/financial-planner-ai-agent:$PYTHONPATH"
   ```

2. **Node.js Build Failures**

   ```bash
   # Solution: Clear cache and reinstall
   cd react_financial_ui
   rm -rf node_modules package-lock.json
   npm install
   npm run build
   ```

3. **Ollama Not Available**
   - Expected on Replit - the app will use fallback mode
   - Gemini evaluator will still work with API key

#### Vercel Issues:

1. **Serverless Function Timeout**

   - Upgrade to Pro plan for longer execution time
   - Optimize AI model calls for faster response

2. **Environment Variables Not Set**

   ```bash
   # Set via Vercel CLI
   vercel env add GEMINI_API_KEY
   ```

3. **Build Failures**
   ```bash
   # Local testing
   cd react_financial_ui
   npm run build
   vercel dev
   ```

### Performance Optimization

#### For Production:

1. **Enable Caching**: Cache AI responses for common queries
2. **Database Optimization**: Use connection pooling
3. **CDN**: Leverage Vercel's global CDN for static assets
4. **Monitoring**: Set up error tracking and performance monitoring

---

## 📞 Support

For deployment issues:

1. Check the deployment logs in Replit/Vercel dashboard
2. Verify environment variables are set correctly
3. Test API endpoints individually
4. Review the troubleshooting section above

---

## 🎉 Success Metrics

After successful deployment, you should see:

- ✅ React UI loads without errors
- ✅ API health check returns 200 status
- ✅ Financial plan generation works
- ✅ WIO Bank platform recommendations display
- ✅ Responsive design on mobile/desktop

**Your Financial Planner AI Agent is now live and ready to help users with intelligent financial planning!** 🚀
