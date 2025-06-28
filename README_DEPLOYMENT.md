# 🚀 Financial Planner AI Agent - Deployment

A comprehensive full-stack AI-powered financial planning application with WIO Bank integration.

## 🌟 Features

- **AI-Powered Recommendations**: Intelligent investment suggestions using Ollama 3.2 + Gemini 2.5 Pro
- **WIO Bank Integration**: Platform-specific recommendations for UAE banking
- **Real-time Analysis**: Live financial planning with risk assessment
- **Responsive UI**: Modern React TypeScript interface with Tailwind CSS
- **Vector Database**: ChromaDB for intelligent data retrieval
- **Multi-platform Deployment**: Ready for Replit and Vercel

## 🚀 Quick Deploy

### Option 1: Replit (Recommended for Development)

1. **Create Replit Project**:
   - Go to [replit.com](https://replit.com)
   - Create new Python Repl
   - Upload all project files

2. **One-Click Setup**:
   ```bash
   bash deploy_replit.sh
   ```

3. **Configure Environment**:
   - Edit `.env` file with your Gemini API key
   - Click "Run" in Replit

### Option 2: Vercel (Recommended for Production)

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Deploy**:
   ```bash
   bash deploy_vercel.sh
   ```

3. **Set Environment Variables**:
   - Add `GEMINI_API_KEY` in Vercel dashboard

## 🔧 Manual Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- Gemini API key

### Local Development
```bash
# 1. Clone and setup
git clone <repository>
cd financial-planner-ai-agent

# 2. Setup Python backend
cd flask_api
pip install -r requirements.txt
python standalone_app.py

# 3. Setup React frontend
cd ../react_financial_ui
npm install
npm start
```

## 📊 Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React UI      │    │   Flask API     │    │   AI Models     │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (Ollama +     │
│                 │    │                 │    │    Gemini)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Static Files  │    │   Vector DB     │    │   Investment    │
│   (Build)       │    │   (ChromaDB)    │    │   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🌐 Deployment Platforms

| Platform | Pros | Cons | Best For |
|----------|------|------|----------|
| **Replit** | Easy setup, Full environment, Real-time collaboration | Limited resources, Slower performance | Development, Demos, Learning |
| **Vercel** | Serverless, Global CDN, Auto-scaling, Professional | Function timeouts, Cold starts | Production, High traffic |

## 🔐 Environment Variables

Required for all deployments:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

Optional:
```bash
OLLAMA_HOST=localhost:11434
OLLAMA_MODEL=llama3.2
FLASK_ENV=production
PORT=3000
```

## 📱 API Endpoints

- `GET /api/health` - Health check
- `POST /api/generate-financial-plan` - Generate financial recommendations

### Example Request:
```json
{
  "goal": "retirement",
  "age": 30,
  "retirement_age": 60,
  "annual_salary": 200000,
  "annual_expenses": 120000,
  "market_type": "UAE",
  "current_savings": 50000,
  "risk_appetite": "moderate"
}
```

## 🎯 Success Checklist

After deployment, verify:

- [ ] Frontend loads at your deployment URL
- [ ] API health check returns 200: `/api/health`
- [ ] Financial plan generation works
- [ ] WIO Bank recommendations display
- [ ] Responsive design on mobile/desktop
- [ ] No console errors in browser

## 🔧 Troubleshooting

### Common Issues:

1. **Import Errors**: Check Python path configuration
2. **Build Failures**: Clear node_modules and reinstall
3. **API Timeouts**: Optimize AI model calls or upgrade plan
4. **Missing Environment Variables**: Verify all required vars are set

### Debug Commands:
```bash
# Test API locally
curl -X GET http://localhost:5001/api/health

# Check React build
cd react_financial_ui && npm run build

# Verify Python imports
python -c "from flask_api.standalone_app import app; print('✅ Imports OK')"
```

## 📞 Support

For deployment issues:
1. Check platform-specific logs (Replit Console / Vercel Dashboard)
2. Verify environment variables
3. Test components individually
4. Review troubleshooting section

## 🎉 What's Next?

After successful deployment:
- Configure custom domain (Vercel)
- Set up monitoring and analytics
- Add user authentication
- Implement caching for better performance
- Scale based on usage patterns

**Your Financial Planner AI Agent is now live! 🚀**
