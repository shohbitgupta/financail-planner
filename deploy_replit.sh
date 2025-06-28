#!/bin/bash

# Financial Planner AI Agent - Replit Deployment Script

echo "🚀 Financial Planner AI Agent - Replit Deployment"
echo "================================================="

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Financial Planner AI Agent Environment Variables
GEMINI_API_KEY=your_gemini_api_key_here
OLLAMA_HOST=localhost:11434
OLLAMA_MODEL=llama3.2
VECTOR_DB_PATH=./enhanced_investment_vector_db
INVESTMENT_DB_PATH=./flask_api/investment_database.db
EOF
    echo "⚠️ Please edit .env file and add your Gemini API key"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r flask_api/requirements.txt
pip install chromadb

# Install Node.js dependencies and build React app
echo "📦 Installing Node.js dependencies..."
cd react_financial_ui
npm install

echo "🔨 Building React application..."
npm run build
cd ..

# Create the unified Replit app
echo "🔧 Creating unified Replit application..."
python deploy_replit.py &

echo ""
echo "✅ Replit deployment setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file and add your Gemini API key"
echo "2. Click 'Run' button in Replit"
echo "3. Your app will be available at the Replit URL"
echo ""
echo "🔗 Features available:"
echo "   - Full-stack Financial Planner AI"
echo "   - WIO Bank platform integration"
echo "   - Real-time AI recommendations"
echo "   - Responsive web interface"
