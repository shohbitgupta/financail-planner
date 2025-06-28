#!/bin/bash

# Financial Planner AI Agent - Vercel Deployment Script

echo "🚀 Financial Planner AI Agent - Vercel Deployment"
echo "=================================================="

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
fi

# Create public directory for static files
mkdir -p public

# Build React application
echo "🔨 Building React application..."
cd react_financial_ui
npm install
npm run build
cd ..

# Copy essential files to API directory
echo "📋 Copying essential files..."
cp flask_api/investment_database.db api/ 2>/dev/null || echo "⚠️ Database file not found"
cp -r enhanced_investment_vector_db api/ 2>/dev/null || echo "⚠️ Vector database not found"

# Create environment variables file for reference
echo "📝 Creating environment variables reference..."
cat > .env.example << EOF
# Financial Planner AI Agent Environment Variables
# Copy this to .env and fill in your actual values

GEMINI_API_KEY=your_gemini_api_key_here
OLLAMA_HOST=localhost:11434
OLLAMA_MODEL=llama3.2

# Database paths (auto-configured for Vercel)
VECTOR_DB_PATH=./enhanced_investment_vector_db
INVESTMENT_DB_PATH=./investment_database.db
EOF

# Deploy to Vercel
echo "🌐 Deploying to Vercel..."
vercel --prod

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Set environment variables in Vercel dashboard:"
echo "   - GEMINI_API_KEY: Your Gemini API key"
echo "2. Test the deployment:"
echo "   - Frontend: Your Vercel URL"
echo "   - API: Your Vercel URL/api/health"
echo "3. Configure custom domain (optional)"
echo ""
echo "🔗 Useful links:"
echo "   - Vercel Dashboard: https://vercel.com/dashboard"
echo "   - Environment Variables: https://vercel.com/docs/concepts/projects/environment-variables"
