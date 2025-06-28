#!/usr/bin/env python3
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
        print("\n🛑 Backend stopped")

if __name__ == "__main__":
    main()
