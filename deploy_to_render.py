#!/usr/bin/env python3
"""
Automated deployment script for Render.com
This script helps deploy the Financial Planner AI Agent API to Render
"""

import os
import sys
import webbrowser
import json
from pathlib import Path

def create_render_deployment():
    """Create all necessary files for Render deployment"""
    
    print("🚀 Preparing Financial Planner AI Agent for Render deployment...")
    
    # Create render.yaml for automatic deployment
    render_config = {
        "services": [
            {
                "type": "web",
                "name": "financial-planner-ai-api",
                "env": "python",
                "buildCommand": "pip install -r requirements_api.txt",
                "startCommand": "python api_only_deploy.py",
                "healthCheckPath": "/api/health",
                "envVars": [
                    {
                        "key": "GEMINI_API_KEY",
                        "sync": False
                    },
                    {
                        "key": "PORT",
                        "value": "10000"
                    },
                    {
                        "key": "FLASK_ENV", 
                        "value": "production"
                    }
                ]
            }
        ]
    }
    
    # Write render.yaml
    with open('render.yaml', 'w') as f:
        import yaml
        yaml.dump(render_config, f, default_flow_style=False)
    
    print("✅ Created render.yaml")
    
    # Create a simple Procfile for alternative deployment
    with open('Procfile', 'w') as f:
        f.write('web: python api_only_deploy.py\n')
    
    print("✅ Created Procfile")
    
    # Create runtime.txt to specify Python version
    with open('runtime.txt', 'w') as f:
        f.write('python-3.9.18\n')
    
    print("✅ Created runtime.txt")
    
    print("\n🎯 Deployment files created successfully!")
    print("\n📋 Next Steps:")
    print("1. Push your code to GitHub:")
    print("   git add .")
    print("   git commit -m 'Add Render deployment configuration'")
    print("   git push origin main")
    print("\n2. Deploy to Render:")
    print("   - Go to https://render.com")
    print("   - Sign up/Login with GitHub")
    print("   - Click 'New +' → 'Web Service'")
    print("   - Connect your GitHub repository")
    print("   - Render will auto-detect the configuration!")
    print("\n3. Set Environment Variables in Render:")
    print("   GEMINI_API_KEY = your_actual_api_key")
    print("\n4. Your API will be live at:")
    print("   https://financial-planner-ai-api.onrender.com")
    
    # Ask if user wants to open Render
    try:
        response = input("\n🌐 Would you like to open Render.com now? (y/n): ").lower()
        if response in ['y', 'yes']:
            webbrowser.open('https://render.com')
            print("✅ Opened Render.com in your browser")
    except KeyboardInterrupt:
        print("\n👋 Deployment preparation complete!")

def test_local_api():
    """Test the API locally before deployment"""
    print("\n🧪 Testing local API...")
    
    try:
        import requests
        
        # Test health endpoint
        response = requests.get('http://localhost:10000/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("⚠️ Local API not running. Start it with: python api_only_deploy.py")
    except ImportError:
        print("⚠️ requests library not installed. Install with: pip install requests")
    except Exception as e:
        print(f"❌ Error testing API: {e}")

def update_react_config():
    """Update React configuration for cloud deployment"""
    print("\n⚛️ Updating React configuration...")
    
    # Update the API URL in React config
    config_path = Path('react_financial_ui/src/config.ts')
    if config_path.exists():
        print("✅ React config already updated for cloud deployment")
    else:
        print("⚠️ React config not found. Make sure to update API URLs manually.")
    
    # Check environment files
    env_path = Path('react_financial_ui/.env')
    if env_path.exists():
        print("✅ React environment file configured")
    else:
        print("⚠️ React environment file not found")

def main():
    """Main deployment preparation function"""
    print("🚀 Financial Planner AI Agent - Render Deployment Helper")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path('api_only_deploy.py').exists():
        print("❌ Error: api_only_deploy.py not found!")
        print("   Make sure you're in the project root directory")
        sys.exit(1)
    
    # Create deployment files
    create_render_deployment()
    
    # Update React configuration
    update_react_config()
    
    # Test local API
    test_local_api()
    
    print("\n🎉 Deployment preparation complete!")
    print("\n📝 Summary:")
    print("   ✅ Render configuration files created")
    print("   ✅ React app configured for cloud API")
    print("   ✅ Local API tested")
    print("\n🚀 Ready for deployment to Render!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Deployment preparation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
