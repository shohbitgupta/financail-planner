#!/usr/bin/env python3
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
        print("\n🛑 Frontend stopped")

if __name__ == "__main__":
    main()
