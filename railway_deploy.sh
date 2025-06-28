#!/bin/bash

echo "🚂 Deploying Financial Planner AI Agent to Railway..."

# Install Railway CLI if not installed
if ! command -v railway &> /dev/null; then
    echo "📦 Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Login to Railway
echo "🔐 Please login to Railway..."
railway login

# Initialize Railway project
echo "🚀 Initializing Railway project..."
railway init

# Set environment variables
echo "🔧 Setting up environment variables..."
echo "Please set your GEMINI_API_KEY in Railway dashboard"

# Deploy
echo "🚀 Deploying to Railway..."
railway up

echo "✅ Deployment complete!"
echo "🌐 Your app will be available at the Railway-provided URL"
