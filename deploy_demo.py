#!/usr/bin/env python3
"""
Demo Deployment Script for Financial Planner AI
Deploys the complete agentic system for demonstration purposes.
"""
import os
import sys
import subprocess
import shutil
import json
import time
from pathlib import Path

class DemoDeployer:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.backend_dir = self.root_dir / "backend"
        self.frontend_dir = self.root_dir / "react_financial_ui"
        self.flask_api_dir = self.root_dir / "flask_api"
        
    def print_step(self, step, message):
        """Print formatted step message."""
        print(f"\n{'='*60}")
        print(f"STEP {step}: {message}")
        print(f"{'='*60}")
    
    def run_command(self, command, cwd=None, check=True):
        """Run shell command with error handling."""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=cwd or self.root_dir,
                capture_output=True,
                text=True,
                check=check
            )
            if result.stdout:
                print(f"✅ {result.stdout.strip()}")
            return result
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {command}")
            print(f"Error: {e.stderr}")
            if check:
                raise
            return e
    
    def check_prerequisites(self):
        """Check if all prerequisites are installed."""
        self.print_step(1, "Checking Prerequisites")
        
        # Check Python
        try:
            python_version = subprocess.check_output([sys.executable, "--version"], text=True).strip()
            print(f"✅ {python_version}")
        except:
            print("❌ Python not found")
            return False
        
        # Check Node.js
        try:
            node_version = subprocess.check_output(["node", "--version"], text=True).strip()
            print(f"✅ Node.js {node_version}")
        except:
            print("❌ Node.js not found. Please install Node.js")
            return False
        
        # Check npm
        try:
            npm_version = subprocess.check_output(["npm", "--version"], text=True).strip()
            print(f"✅ npm {npm_version}")
        except:
            print("❌ npm not found")
            return False
        
        # Check if Ollama is running
        try:
            result = subprocess.run(
                ["curl", "-s", "http://localhost:11434/api/tags"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print("✅ Ollama is running")
            else:
                print("⚠️  Ollama not running. Please start Ollama service")
                print("   Run: ollama serve")
        except:
            print("⚠️  Could not check Ollama status")
        
        return True
    
    def setup_environment(self):
        """Set up environment variables and configuration."""
        self.print_step(2, "Setting Up Environment")
        
        # Create .env file for Flask API
        env_content = """# Financial Planner AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
FLASK_ENV=development
FLASK_DEBUG=True
"""
        
        env_file = self.flask_api_dir / ".env"
        with open(env_file, "w") as f:
            f.write(env_content)
        print(f"✅ Created environment file: {env_file}")
        
        # Create backend environment
        backend_env = self.backend_dir / ".env"
        backend_env_content = """# Backend Configuration
FLASK_ENV=development
GEMINI_API_KEY=your_gemini_api_key_here
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
VECTOR_DB_PATH=data/databases/vector_db
INVESTMENT_DB_PATH=data/databases/investment.db
"""
        with open(backend_env, "w") as f:
            f.write(backend_env_content)
        print(f"✅ Created backend environment file: {backend_env}")
    
    def setup_databases(self):
        """Set up required databases."""
        self.print_step(3, "Setting Up Databases")
        
        # Create backend data directories
        backend_data_dir = self.backend_dir / "data" / "databases"
        backend_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy existing databases if they exist
        if (self.root_dir / "investment_database.db").exists():
            shutil.copy2(
                self.root_dir / "investment_database.db",
                backend_data_dir / "investment.db"
            )
            print("✅ Copied investment database to backend")
        
        if (self.root_dir / "enhanced_investment_vector_db").exists():
            if (backend_data_dir / "vector_db").exists():
                shutil.rmtree(backend_data_dir / "vector_db")
            shutil.copytree(
                self.root_dir / "enhanced_investment_vector_db",
                backend_data_dir / "vector_db"
            )
            print("✅ Copied vector database to backend")
        
        # Copy databases to flask_api for compatibility
        if (self.root_dir / "investment_database.db").exists():
            shutil.copy2(
                self.root_dir / "investment_database.db",
                self.flask_api_dir / "investment_database.db"
            )
            print("✅ Copied investment database to flask_api")
    
    def install_dependencies(self):
        """Install Python and Node.js dependencies."""
        self.print_step(4, "Installing Dependencies")

        # Install core Python dependencies individually to handle conflicts
        print("Installing core Python dependencies...")
        core_deps = [
            "flask==2.3.3",
            "flask-cors==4.0.0",
            "requests==2.31.0",
            "numpy",
            "pandas",
            "scipy"
        ]

        for dep in core_deps:
            try:
                self.run_command(f"pip install {dep}", check=False)
            except:
                print(f"⚠️  Could not install {dep}, continuing...")

        # Install LangChain dependencies
        print("Installing LangChain dependencies...")
        langchain_deps = [
            "langchain-ollama",
            "langchain-core",
            "langchain-chroma"
        ]

        for dep in langchain_deps:
            try:
                self.run_command(f"pip install {dep}", check=False)
            except:
                print(f"⚠️  Could not install {dep}, continuing...")

        # Install optional dependencies
        print("Installing optional dependencies...")
        try:
            self.run_command("pip install google-generativeai", check=False)
        except:
            print("⚠️  Could not install google-generativeai (optional for evaluator)")

        # Install Node.js dependencies
        print("Installing React UI dependencies...")
        if (self.frontend_dir / "package.json").exists():
            try:
                self.run_command("npm install", cwd=self.frontend_dir)
            except:
                print("⚠️  Node.js dependency installation failed, but continuing...")
    
    def create_startup_scripts(self):
        """Create startup scripts for easy demo launch."""
        self.print_step(5, "Creating Startup Scripts")
        
        # Create backend startup script
        backend_script = self.root_dir / "start_backend.py"
        backend_script_content = '''#!/usr/bin/env python3
"""Start the Flask API backend for demo."""
import subprocess
import sys
import os
from pathlib import Path

def start_backend():
    """Start the Flask backend."""
    flask_api_dir = Path(__file__).parent / "flask_api"
    
    print("🚀 Starting Financial Planner AI Backend...")
    print("📍 Backend will be available at: http://localhost:5000")
    print("📊 Health check: http://localhost:5000/health")
    print("💡 API docs: http://localhost:5000/")
    print("\\n" + "="*50)
    
    try:
        # Change to flask_api directory and run
        os.chdir(flask_api_dir)
        subprocess.run([sys.executable, "standalone_app.py"], check=True)
    except KeyboardInterrupt:
        print("\\n🛑 Backend stopped by user")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")

if __name__ == "__main__":
    start_backend()
'''
        
        with open(backend_script, "w") as f:
            f.write(backend_script_content)
        backend_script.chmod(0o755)
        print(f"✅ Created backend startup script: {backend_script}")
        
        # Create frontend startup script
        frontend_script = self.root_dir / "start_frontend.py"
        frontend_script_content = '''#!/usr/bin/env python3
"""Start the React frontend for demo."""
import subprocess
import sys
import os
from pathlib import Path

def start_frontend():
    """Start the React frontend."""
    frontend_dir = Path(__file__).parent / "react_financial_ui"
    
    print("🚀 Starting Financial Planner AI Frontend...")
    print("📍 Frontend will be available at: http://localhost:3000")
    print("💡 Make sure backend is running at: http://localhost:5000")
    print("\\n" + "="*50)
    
    try:
        # Change to frontend directory and run
        os.chdir(frontend_dir)
        subprocess.run(["npm", "start"], check=True)
    except KeyboardInterrupt:
        print("\\n🛑 Frontend stopped by user")
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")

if __name__ == "__main__":
    start_frontend()
'''
        
        with open(frontend_script, "w") as f:
            f.write(frontend_script_content)
        frontend_script.chmod(0o755)
        print(f"✅ Created frontend startup script: {frontend_script}")
    
    def create_demo_launcher(self):
        """Create a comprehensive demo launcher."""
        self.print_step(6, "Creating Demo Launcher")
        
        launcher_script = self.root_dir / "launch_demo.py"
        launcher_content = '''#!/usr/bin/env python3
"""
Financial Planner AI - Demo Launcher
Launches both backend and frontend for demonstration.
"""
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
import threading

def start_backend():
    """Start backend in a separate process."""
    try:
        subprocess.run([sys.executable, "start_backend.py"], cwd=Path(__file__).parent)
    except Exception as e:
        print(f"Backend error: {e}")

def start_frontend():
    """Start frontend in a separate process."""
    try:
        time.sleep(3)  # Wait for backend to start
        subprocess.run([sys.executable, "start_frontend.py"], cwd=Path(__file__).parent)
    except Exception as e:
        print(f"Frontend error: {e}")

def main():
    """Launch the complete demo."""
    print("🎯 Financial Planner AI - Demo Launcher")
    print("="*50)
    print("This will start both backend and frontend services.")
    print("\\n📋 Prerequisites:")
    print("  ✓ Ollama running (ollama serve)")
    print("  ✓ Python dependencies installed")
    print("  ✓ Node.js dependencies installed")
    print("\\n🚀 Starting services...")
    
    # Start backend in background thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Wait a bit then start frontend
    time.sleep(5)
    
    print("\\n🌐 Opening browser...")
    try:
        webbrowser.open("http://localhost:3000")
    except:
        print("Could not open browser automatically")
        print("Please open: http://localhost:3000")
    
    # Start frontend (this will block)
    start_frontend()

if __name__ == "__main__":
    main()
'''
        
        with open(launcher_script, "w") as f:
            f.write(launcher_content)
        launcher_script.chmod(0o755)
        print(f"✅ Created demo launcher: {launcher_script}")

def main():
    """Main deployment function."""
    deployer = DemoDeployer()
    
    print("🎯 Financial Planner AI - Demo Deployment")
    print("="*60)
    print("This script will set up the complete agentic system for demo.")
    
    try:
        # Run deployment steps
        if not deployer.check_prerequisites():
            print("❌ Prerequisites check failed. Please install missing components.")
            return 1
        
        deployer.setup_environment()
        deployer.setup_databases()
        deployer.install_dependencies()
        deployer.create_startup_scripts()
        deployer.create_demo_launcher()
        
        print("\n" + "="*60)
        print("🎉 DEPLOYMENT COMPLETE!")
        print("="*60)
        print("\n📋 Next Steps:")
        print("1. Start Ollama: ollama serve")
        print("2. Pull required model: ollama pull llama3.2")
        print("3. (Optional) Set GEMINI_API_KEY in .env files for evaluator")
        print("4. Launch demo: python launch_demo.py")
        print("\n🌐 URLs:")
        print("  Frontend: http://localhost:3000")
        print("  Backend:  http://localhost:5000")
        print("\n💡 Individual startup:")
        print("  Backend:  python start_backend.py")
        print("  Frontend: python start_frontend.py")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
