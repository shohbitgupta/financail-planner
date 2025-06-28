#!/usr/bin/env python3
"""
Setup script for the Financial Plan Evaluator Agent
This script helps configure the Gemini API key for the evaluator
"""

import os

def setup_gemini_api_key():
    """Setup Gemini API key for the evaluator agent"""
    print("🔧 Setting up Financial Plan Evaluator Agent with Gemini 2.5 Pro")
    print("=" * 60)
    
    # Check if API key is already set
    current_key = os.getenv('GEMINI_API_KEY')
    if current_key:
        print(f"✅ GEMINI_API_KEY is already set: {current_key[:10]}...")
        return True
    
    print("\n📋 To use the evaluator agent, you need a Gemini API key.")
    print("   1. Go to: https://aistudio.google.com/app/apikey")
    print("   2. Create a new API key")
    print("   3. Copy the API key")
    print()
    
    # Get API key from user
    api_key = "AIzaSyBAK741U0ImBRfHgsuPhKFIQrehP1j1_yU"
    
    if not api_key:
        print("❌ No API key provided. Evaluator agent will not be available.")
        return False
    
    # Set environment variable for current session
    os.environ['GEMINI_API_KEY'] = current_key
    
    # Create .env file for persistence
    env_file_path = os.path.join(os.path.dirname(__file__), '.env')
    try:
        with open(env_file_path, 'w') as f:
            f.write(f"GEMINI_API_KEY={api_key}\n")
        print(f"✅ API key saved to {env_file_path}")
    except Exception as e:
        print(f"⚠️  Could not save to .env file: {e}")
    
    # Test the API key
    print("\n🧪 Testing Gemini API connection...")
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Simple test
        response = model.generate_content("Hello, respond with 'API test successful'")
        if "successful" in response.text.lower():
            print("✅ Gemini API connection successful!")
            return True
        else:
            print("⚠️  Unexpected response from Gemini API")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Gemini API: {e}")
        print("   Please check your API key and try again.")
        return False

def load_env_file():
    """Load environment variables from .env file"""
    env_file_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file_path):
        try:
            with open(env_file_path, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
            print(f"✅ Loaded environment variables from {env_file_path}")
            return True
        except Exception as e:
            print(f"⚠️  Error loading .env file: {e}")
    return False

def main():
    """Main setup function"""
    print("🚀 Financial Plan Evaluator Agent Setup")
    print("=" * 50)
    
    # Try to load existing .env file
    if load_env_file():
        current_key = os.getenv('GEMINI_API_KEY')
        if current_key:
            print(f"✅ Found existing API key: {current_key[:10]}...")
            
            # Test existing key
            try:
                import google.generativeai as genai
                genai.configure(api_key=current_key)
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                response = model.generate_content("Test")
                if response and response.text:
                    print("✅ Existing API key is working!")
                    return
                else:
                    print("⚠️ API key test failed - no response")
                    raise Exception("No response from API")
            except Exception as e:
                print(f"❌ Existing API key failed: {e}")
                print("   Setting up new API key...")
    
    # Setup new API key
    if setup_gemini_api_key():
        print("\n🎉 Evaluator agent setup complete!")
        print("\n📖 How it works:")
        print("   1. Llama 3.2 generates initial financial plan")
        print("   2. Gemini 2.5 Pro evaluates the response quality")
        print("   3. If score < 8.0, Gemini generates improved response")
        print("   4. Final response is returned to the user")
        print("\n🔄 Restart the Flask API to use the evaluator agent.")
    else:
        print("\n❌ Setup failed. Evaluator agent will not be available.")
        print("   The system will still work with Llama 3.2 only.")

if __name__ == "__main__":
    main()
