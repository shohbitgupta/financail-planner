#!/usr/bin/env python3
"""
Quick Demo Setup for Financial Planner AI
Minimal setup to get the demo running quickly.
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_step(step, message):
    """Print formatted step message."""
    print(f"\n{'='*50}")
    print(f"STEP {step}: {message}")
    print(f"{'='*50}")

def run_command(command, cwd=None):
    """Run command and return success status."""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {command}")
            return True
        else:
            print(f"⚠️  {command} (non-critical)")
            return False
    except Exception as e:
        print(f"⚠️  {command} failed: {e}")
        return False

def main():
    """Quick setup for demo."""
    root_dir = Path(__file__).parent
    flask_api_dir = root_dir / "flask_api"
    frontend_dir = root_dir / "react_financial_ui"
    
    print("🚀 Financial Planner AI - Quick Demo Setup")
    print("="*50)
    
    # Step 1: Check Ollama
    print_step(1, "Checking Ollama")
    try:
        result = subprocess.run(["curl", "-s", "http://localhost:11434/api/tags"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Ollama is running")
        else:
            print("❌ Ollama not running. Please start: ollama serve")
            return 1
    except:
        print("❌ Ollama not accessible. Please start: ollama serve")
        return 1
    
    # Step 2: Setup environment
    print_step(2, "Setting Up Environment")
    
    # Create .env for flask_api
    env_content = """GEMINI_API_KEY=your_gemini_api_key_here
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
FLASK_ENV=development
"""
    
    with open(flask_api_dir / ".env", "w") as f:
        f.write(env_content)
    print("✅ Created flask_api/.env")
    
    # Step 3: Copy databases
    print_step(3, "Setting Up Databases")
    
    if (root_dir / "investment_database.db").exists():
        shutil.copy2(root_dir / "investment_database.db", flask_api_dir / "investment_database.db")
        print("✅ Copied investment database")
    else:
        print("⚠️  Investment database not found")
    
    # Step 4: Install minimal dependencies
    print_step(4, "Installing Core Dependencies")
    
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if not in_venv:
        print("⚠️  Not in virtual environment. Consider using: python -m venv venv && source venv/bin/activate")
    
    # Install only essential packages
    essential_packages = [
        "flask",
        "flask-cors", 
        "requests"
    ]
    
    for package in essential_packages:
        run_command(f"pip install {package}")
    
    # Try to install langchain packages
    langchain_packages = ["langchain-ollama", "langchain-core"]
    for package in langchain_packages:
        run_command(f"pip install {package}")
    
    # Step 5: Install Node dependencies
    print_step(5, "Installing Node Dependencies")
    if frontend_dir.exists():
        run_command("npm install", cwd=frontend_dir)
    
    # Step 6: Create startup scripts
    print_step(6, "Creating Startup Scripts")
    
    # Simple backend starter
    backend_starter = root_dir / "start_demo_backend.py"
    with open(backend_starter, "w") as f:
        f.write('''#!/usr/bin/env python3
import subprocess
import sys
import os
from pathlib import Path

def main():
    flask_api_dir = Path(__file__).parent / "flask_api"
    print("🚀 Starting Financial Planner Backend...")
    print("📍 Backend: http://localhost:5000")
    print("📊 Health: http://localhost:5000/health")
    
    try:
        os.chdir(flask_api_dir)
        subprocess.run([sys.executable, "standalone_app.py"])
    except KeyboardInterrupt:
        print("\\n🛑 Backend stopped")

if __name__ == "__main__":
    main()
''')
    backend_starter.chmod(0o755)
    print("✅ Created start_demo_backend.py")
    
    # Simple frontend starter
    frontend_starter = root_dir / "start_demo_frontend.py"
    with open(frontend_starter, "w") as f:
        f.write('''#!/usr/bin/env python3
import subprocess
import os
from pathlib import Path

def main():
    frontend_dir = Path(__file__).parent / "react_financial_ui"
    print("🚀 Starting Financial Planner Frontend...")
    print("📍 Frontend: http://localhost:3000")
    
    try:
        os.chdir(frontend_dir)
        subprocess.run(["npm", "start"])
    except KeyboardInterrupt:
        print("\\n🛑 Frontend stopped")

if __name__ == "__main__":
    main()
''')
    frontend_starter.chmod(0o755)
    print("✅ Created start_demo_frontend.py")
    
    # Step 7: Final instructions
    print("\n" + "="*50)
    print("🎉 QUICK SETUP COMPLETE!")
    print("="*50)
    print("\n📋 To start the demo:")
    print("1. Ensure Ollama is running: ollama serve")
    print("2. Pull model if needed: ollama pull llama3.2")
    print("3. Start backend: python start_demo_backend.py")
    print("4. Start frontend: python start_demo_frontend.py")
    print("5. Open browser: http://localhost:3000")
    
    print("\n💡 Optional:")
    print("- Set GEMINI_API_KEY in flask_api/.env for evaluator features")
    print("- Check logs in terminal for any issues")
    
    print("\n🌐 Demo URLs:")
    print("  Frontend: http://localhost:3000")
    print("  Backend:  http://localhost:5000")
    print("  Health:   http://localhost:5000/health")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
