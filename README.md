# 🤖 Financial Planner AI Agent

A comprehensive AI-powered financial planning system that combines local LLM capabilities with professional investment analysis to provide personalized financial recommendations for UAE and US markets.

## 🌟 Features

### 🎯 Core Capabilities
- **AI-Powered Financial Planning** - Ollama 3.2 LLM for intelligent financial advice
- **Interactive Chat Interface** - Natural conversation-based goal setting
- **Comprehensive Market Analysis** - 33+ instruments across UAE and US markets
- **Risk Assessment & Portfolio Optimization** - Modern Portfolio Theory implementation
- **Goal Achievement Timeline** - Detailed projections with risk analysis
- **Platform Integration** - WIO Bank product recommendations for UAE market

### 🧠 AI & Machine Learning
- **Local LLM Integration** - Ollama 3.2 for privacy-focused AI responses
- **Vector Database** - ChromaDB with comprehensive historical market data
- **AI Evaluator Agent** - Gemini 2.5 Pro for response quality assessment
- **Intelligent Recommendations** - Context-aware investment suggestions

### 🏗️ Technical Architecture
- **Frontend** - React with TypeScript, Tailwind CSS
- **Backend** - Flask API with modular architecture
- **Database** - SQLite for structured data, ChromaDB for vector storage
- **Deployment** - Ready for Replit, Vercel, and local hosting

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Ollama installed locally
- Gemini API key (optional, for evaluator agent)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd local_ai_agent
cp .env.example .env
# Edit .env with your API keys
```

### 2. Install Dependencies
```bash
# Python dependencies
pip install -r requirements.txt

# React dependencies
cd react_financial_ui
npm install
cd ..
```

### 3. Setup Ollama
```bash
# Install and start Ollama
ollama pull llama3.2
ollama serve
```

### 4. Run the Application
```bash
# Simple deployment (recommended)
python simple_deploy.py

# Or use the full deployment script
python deploy_replit.py
```

### 5. Access the Application
- **Web Interface**: http://localhost:3000
- **API Health**: http://localhost:3000/api/health

## 📁 Project Structure

```
local_ai_agent/
├── 🎨 react_financial_ui/          # React frontend
│   ├── src/components/             # UI components
│   ├── public/                     # Static assets
│   └── package.json               # Dependencies
├── 🔧 flask_api/                  # Flask backend
│   ├── standalone_app.py          # Main API application
│   ├── evaluator_agent.py         # AI evaluator
│   └── requirements.txt           # Python dependencies
├── 🗄️ backend/                    # Structured backend (alternative)
│   ├── app/                       # Application modules
│   ├── services/                  # Business logic
│   └── utils/                     # Helper functions
├── 🚀 api/                        # Serverless functions (Vercel)
├── 📊 Database Files
│   ├── investment_database.db     # SQLite database
│   └── enhanced_investment_vector_db/ # ChromaDB
├── 🛠️ Core Modules
│   ├── investment_database.py     # Database management
│   ├── portfolio_optimizer.py     # Portfolio optimization
│   ├── financial_calculator.py    # Financial calculations
│   ├── risk_assessment.py         # Risk analysis
│   └── vectors.py                 # Vector database operations
└── 📋 Deployment
    ├── simple_deploy.py           # Simple deployment script
    ├── deploy_replit.py           # Replit deployment
    ├── vercel.json                # Vercel configuration
    └── .replit                    # Replit configuration
```

## 🌐 Deployment Options

### 🔧 Local Development
```bash
python simple_deploy.py
```

### ☁️ Replit (Recommended for Demo)
1. Import repository to Replit
2. Set environment variables in Secrets
3. Run the project

### ⚡ Vercel (Production)
```bash
npm install -g vercel
vercel login
vercel deploy
```

### 🐳 Docker (Coming Soon)
```bash
docker build -t financial-planner .
docker run -p 3000:3000 financial-planner
```

## 🔧 Configuration

### Environment Variables
```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
DATABASE_PATH=./investment_database.db
VECTOR_DB_PATH=./enhanced_investment_vector_db
```

### API Endpoints
- `GET /api/health` - Health check
- `POST /api/generate-financial-plan` - Generate financial plan
- `GET /` - React application

## 🧪 Testing

```bash
# Test the enhanced planner
python test_enhanced_planner.py

# Test platform recommendations
python test_platform_recommendations.py

# Test evaluator agent
cd flask_api && python test_evaluator.py
```

## 📊 Data Sources

### Market Data
- **UAE Markets**: ADX General Historical Data, DFMGI Daily Closing
- **US Markets**: Major indices, ETFs, and individual stocks
- **Fixed Income**: Bonds, REITs, and money market instruments

### AI Models
- **Primary LLM**: Ollama 3.2 (Local)
- **Evaluator**: Gemini 2.5 Pro (Cloud)
- **Vector Database**: ChromaDB with financial embeddings

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Ollama** for local LLM capabilities
- **Google Gemini** for AI evaluation
- **WIO Bank** for UAE market integration
- **Modern Portfolio Theory** for optimization algorithms

## 📞 Support

For support, please open an issue in the GitHub repository or contact the development team.

---

**Built with ❤️ for intelligent financial planning**
