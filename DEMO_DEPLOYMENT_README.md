# Financial Planner AI - Demo Deployment Guide

🎯 **Complete Agentic Financial Planning System**

This guide will help you deploy the complete Financial Planner AI system for demonstration purposes. The system includes:

- 🤖 **Ollama 3.2 LLM** for financial planning generation
- 🔍 **Vector Database** with 37 investment instruments (UAE/US markets)
- 📊 **Portfolio Optimization** using Modern Portfolio Theory
- 🎯 **Risk Assessment** and goal-based planning
- 🔬 **Gemini 2.5 Pro Evaluator** for response improvement
- 🌐 **React UI** with professional dashboard
- 🚀 **Flask API** backend with clean architecture

## 🚀 Quick Start (Automated Deployment)

### 1. Prerequisites

**Required Software:**
- Python 3.8+ 
- Node.js 16+
- npm
- Ollama

**Install Ollama:**
```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows - Download from https://ollama.ai
```

### 2. Deploy the System

```bash
# Clone/navigate to the project directory
cd local_ai_agent

# Run automated deployment
python deploy_demo.py
```

The deployment script will:
- ✅ Check prerequisites
- ✅ Set up environment variables
- ✅ Copy databases to correct locations
- ✅ Install Python and Node.js dependencies
- ✅ Create startup scripts
- ✅ Generate demo launcher

### 3. Start Services

**Option A: Complete Demo Launcher**
```bash
# Start Ollama first
ollama serve

# Pull required model
ollama pull llama3.2

# Launch complete demo (opens browser automatically)
python launch_demo.py
```

**Option B: Manual Startup**
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start Backend
python start_backend.py

# Terminal 3: Start Frontend  
python start_frontend.py

# Open browser: http://localhost:3000
```

## 🌐 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | React UI Dashboard |
| **Backend API** | http://localhost:5000 | Flask API |
| **Health Check** | http://localhost:5000/health | Service status |
| **API Docs** | http://localhost:5000/ | API information |

## 🎮 Demo Features

### 1. Financial Planning Input
- **User Profile**: Age, retirement age, salary, expenses
- **Goals**: Retirement, house purchase, education
- **Risk Tolerance**: Conservative, moderate, aggressive
- **Market Preference**: UAE, US, Global
- **Sharia Compliance**: Optional filtering

### 2. AI-Generated Recommendations
- **Specific Instruments**: Tesla stock, UAE bonds, REITs
- **Portfolio Allocation**: Optimized using Modern Portfolio Theory
- **Risk Analysis**: Detailed risk assessment
- **Timeline Planning**: Goal achievement projections

### 3. Advanced Features
- **Expandable Details**: Click instruments for detailed analysis
- **Historical Data**: Performance metrics and projections
- **Evaluator Insights**: Gemini 2.5 Pro evaluation (if API key provided)
- **Real-time LLM**: Actual Ollama 3.2 responses

## ⚙️ Configuration

### Environment Variables

**Flask API (.env in flask_api/):**
```env
GEMINI_API_KEY=your_gemini_api_key_here
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
FLASK_ENV=development
```

**Backend (.env in backend/):**
```env
FLASK_ENV=development
GEMINI_API_KEY=your_gemini_api_key_here
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
VECTOR_DB_PATH=data/databases/vector_db
INVESTMENT_DB_PATH=data/databases/investment.db
```

### Optional: Gemini API Setup

For enhanced evaluator features:

1. Get Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Update `GEMINI_API_KEY` in both .env files
3. Restart services

## 🗄️ Database Information

### Investment Database
- **33 Instruments**: Stocks, bonds, REITs, commodities
- **Markets**: UAE (ADX, DFM), US (NYSE, NASDAQ)
- **Metrics**: Expected returns, risk levels, Sharpe ratios
- **Compliance**: Sharia and ESG filtering

### Vector Database
- **37 Documents**: Detailed instrument profiles
- **Embeddings**: Ollama-based semantic search
- **Context**: Historical data, analysis, recommendations

## 🔧 Troubleshooting

### Common Issues

**1. Ollama Not Running**
```bash
# Start Ollama service
ollama serve

# Check if running
curl http://localhost:11434/api/tags
```

**2. Model Not Found**
```bash
# Pull the required model
ollama pull llama3.2

# List available models
ollama list
```

**3. Port Conflicts**
```bash
# Check what's using ports
lsof -i :3000  # Frontend
lsof -i :5000  # Backend
lsof -i :11434 # Ollama
```

**4. Dependencies Issues**
```bash
# Reinstall Python dependencies
pip install -r requirements.txt
pip install -r flask_api/requirements.txt

# Reinstall Node dependencies
cd react_financial_ui
rm -rf node_modules package-lock.json
npm install
```

**5. Database Issues**
```bash
# Re-run deployment to copy databases
python deploy_demo.py
```

### Logs and Debugging

**Backend Logs:**
- Flask API logs appear in terminal
- Check for Ollama connection status
- Vector database initialization messages

**Frontend Logs:**
- Browser console (F12)
- Network tab for API call status
- React development server logs

## 📊 Demo Scenarios

### Scenario 1: Young Professional
- Age: 28, Retirement: 65
- Salary: $80,000, Expenses: $50,000
- Goals: Retirement, house purchase
- Risk: Moderate

**Expected Output:**
- Growth-focused portfolio (70% equity, 30% bonds)
- Specific recommendations: Tesla, UAE growth stocks
- 37-year investment timeline

### Scenario 2: Conservative Investor
- Age: 45, Retirement: 60
- Salary: $120,000, Expenses: $80,000
- Goals: Retirement, children's education
- Risk: Conservative, Sharia-compliant

**Expected Output:**
- Balanced portfolio (40% equity, 60% bonds/sukuk)
- Sharia-compliant instruments only
- 15-year focused planning

### Scenario 3: Aggressive Growth
- Age: 25, Retirement: 65
- Salary: $60,000, Expenses: $35,000
- Goals: Wealth building, early retirement
- Risk: Aggressive

**Expected Output:**
- High-growth portfolio (85% equity, 15% alternatives)
- Tech stocks, growth REITs
- Long-term compound growth strategy

## 🎯 Demo Tips

1. **Start with Ollama**: Always ensure Ollama is running first
2. **Wait for Initialization**: Backend needs time to load vector database
3. **Try Different Scenarios**: Test various user profiles
4. **Explore Details**: Click on recommended instruments
5. **Check Evaluator**: If Gemini API key is set, check Details tab
6. **Monitor Logs**: Watch terminal output for system status

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React UI      │    │   Flask API     │    │   Ollama LLM    │
│   (Port 3000)   │◄──►│   (Port 5000)   │◄──►│   (Port 11434)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Vector DB +    │
                    │  Investment DB  │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Gemini 2.5 Pro │
                    │   (Evaluator)   │
                    └─────────────────┘
```

## 📞 Support

If you encounter issues during demo deployment:

1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Ensure Ollama is running and model is pulled
4. Check terminal logs for specific error messages
5. Re-run `python deploy_demo.py` if needed

---

🎉 **Ready to demonstrate the complete Financial Planner AI system!**
