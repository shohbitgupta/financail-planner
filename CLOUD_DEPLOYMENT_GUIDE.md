# 🚀 Cloud Deployment Guide - Financial Planner AI Agent

## 📋 Quick Deployment Steps

### 🔥 **OPTION 1: Deploy API to Render (FREE)**

#### Step 1: Create GitHub Repository
```bash
# If you haven't already, push to GitHub
git add .
git commit -m "Add cloud deployment configuration"
git remote add origin https://github.com/YOUR_USERNAME/financial-planner-ai.git
git push -u origin main
```

#### Step 2: Deploy to Render
1. **Go to**: https://render.com
2. **Sign up/Login** with GitHub
3. **Click "New +"** → **"Web Service"**
4. **Connect Repository**: Select your `financial-planner-ai` repo
5. **Configure Service**:
   - **Name**: `financial-planner-ai-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements_api.txt`
   - **Start Command**: `python api_only_deploy.py`
   - **Instance Type**: `Free`

#### Step 3: Set Environment Variables
In Render dashboard → Environment:
```
GEMINI_API_KEY=your_actual_gemini_api_key_here
PORT=10000
FLASK_ENV=production
```

#### Step 4: Deploy
- Click **"Create Web Service"**
- Wait 5-10 minutes for deployment
- Your API will be live at: `https://financial-planner-ai-api.onrender.com`

---

### 🔥 **OPTION 2: Deploy to Railway (FREE $5 Credit)**

#### Step 1: Install Railway CLI
```bash
npm install -g @railway/cli
```

#### Step 2: Deploy
```bash
# Login to Railway
railway login

# Initialize project
railway init

# Set environment variables
railway variables set GEMINI_API_KEY=your_api_key_here

# Deploy
railway up
```

---

## 🔧 **Update React App to Use Cloud API**

### Your React app is already configured! 

The following files have been updated:
- ✅ `react_financial_ui/src/config.ts` - API configuration
- ✅ `react_financial_ui/src/components/FinancialPlannerDashboard.tsx` - Updated API calls
- ✅ `react_financial_ui/.env` - Environment variables
- ✅ `react_financial_ui/.env.production` - Production environment

### Test Your Deployment

1. **Test API Health**:
   ```bash
   curl https://your-app-name.onrender.com/api/health
   ```

2. **Test Financial Plan Generation**:
   ```bash
   curl -X POST https://your-app-name.onrender.com/api/generate-financial-plan \
     -H "Content-Type: application/json" \
     -d '{"user_input": "I am 30 years old, earn $50000 annually, want to retire at 60"}'
   ```

3. **Update React Environment**:
   ```bash
   # Update the API URL in react_financial_ui/.env
   REACT_APP_API_URL=https://your-actual-render-url.onrender.com
   ```

4. **Rebuild React App**:
   ```bash
   cd react_financial_ui
   npm run build
   cd ..
   python simple_deploy.py
   ```

---

## 🎯 **Current Status**

### ✅ **Ready for Deployment**:
- `api_only_deploy.py` - Lightweight API server
- `requirements_api.txt` - Minimal dependencies
- `render.yaml` - Render configuration
- React app configured with cloud API URLs

### 🔄 **API Endpoints Available**:
- `GET /api/health` - Health check
- `POST /api/generate-financial-plan` - Generate financial plan
- `GET /` - API information

### 🌐 **Expected URLs After Deployment**:
- **API**: `https://financial-planner-ai-api.onrender.com`
- **Health Check**: `https://financial-planner-ai-api.onrender.com/api/health`
- **Generate Plan**: `https://financial-planner-ai-api.onrender.com/api/generate-financial-plan`

---

## 🚨 **Important Notes**

1. **Free Tier Limitations**:
   - Render: 750 hours/month, sleeps after 15 min inactivity
   - Railway: $5 credit/month

2. **API Response Time**:
   - First request may take 30-60 seconds (cold start)
   - Subsequent requests: 2-5 seconds

3. **Environment Variables**:
   - Always set `GEMINI_API_KEY` in deployment platform
   - Never commit `.env` files with real API keys

4. **Monitoring**:
   - Check deployment logs in platform dashboard
   - Monitor API health endpoint

---

## 🎉 **Next Steps**

1. **Deploy API** using Option 1 or 2 above
2. **Update React environment** with your actual API URL
3. **Test the integration** 
4. **Share your live demo** with the deployed URL!

Your Financial Planner AI Agent will be **live on the internet** and accessible from anywhere! 🌍
