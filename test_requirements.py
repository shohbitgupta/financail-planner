#!/usr/bin/env python3
"""
Test script to verify requirements.txt dependencies work correctly
"""

import sys

def test_requirements():
    """Test that all required packages can be imported"""
    
    print("🧪 Testing requirements.txt dependencies...")
    
    try:
        import flask
        print(f"✅ Flask: {flask.__version__}")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        import flask_cors
        print(f"✅ Flask-CORS: Available")
    except ImportError as e:
        print(f"❌ Flask-CORS import failed: {e}")
        return False
    
    try:
        import dotenv
        print(f"✅ python-dotenv: Available")
    except ImportError as e:
        print(f"❌ python-dotenv import failed: {e}")
        return False
    
    try:
        import requests
        print(f"✅ requests: {requests.__version__}")
    except ImportError as e:
        print(f"❌ requests import failed: {e}")
        return False
    
    try:
        import google.generativeai as genai
        print(f"✅ google-generativeai: Available")
    except ImportError as e:
        print(f"❌ google-generativeai import failed: {e}")
        return False
    
    try:
        import werkzeug
        print(f"✅ Werkzeug: {werkzeug.__version__}")
    except ImportError as e:
        print(f"❌ Werkzeug import failed: {e}")
        return False
    
    print("\n🎉 All requirements.txt dependencies are working!")
    return True

if __name__ == "__main__":
    success = test_requirements()
    sys.exit(0 if success else 1)
