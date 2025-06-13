#!/usr/bin/env python3
import subprocess
import sys
import time
import os
import threading
from dotenv import load_dotenv

def check_environment():
    """Check if environment is set up correctly"""
    print("Checking Environment...")
    
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY not found!")
        print("Please create a .env file with:")
        print("OPENAI_API_KEY=your_openai_api_key_here")
        return False
    
    print("OpenAI API key found ...")
    
    pdf_path = '/Users/omkarsatapaphy/Downloads/Apple Laptop FAQ.pdf'
    if not os.path.exists(pdf_path):
        print(f"⚠️  FAQ PDF not found at: {pdf_path}")
        print("Please update the path in tools.py (line 34)")
        print("You can still test with other features")
    else:
        print("FAQ PDF found")
    
    return True

def run_api():
    """Run Flask API"""
    try:
        print("Starting Flask API...")
        subprocess.run([sys.executable, "api.py"])
    except KeyboardInterrupt:
        print("API stopped")

def run_frontend():
    """Run Streamlit frontend"""
    try:
        print("🎨 Starting Streamlit frontend...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py", "--server.port=8501"])
    except KeyboardInterrupt:
        print("Frontend stopped")

def main():
    print("Lumi AI Assistant Launcher")
    print("=" * 50)
    
    if not check_environment():
        return
    
    print("\nChoose how to run:")
    print("1. Run API Only (port 5001)")
    print("2. Run Frontend Only (port 8501)")
    print("3. Run Both")
    print("4. Exit")
    
    choice = 3 # hard coding for demo
    
    if choice == "1":
        print("\nStarting API only...")
        print("API: http://localhost:5001")
        run_api()
    
    elif choice == "2":
        print("\nStarting Frontend only...")
        print("Make sure API is running on port 5001")
        print("Frontend: http://localhost:8501")
        run_frontend()
    
    elif choice == "3":
        print("\nStarting both services...")
        print("API: http://localhost:5001")
        print("Frontend: http://localhost:8501")
        print("Press Ctrl+C to stop both")
        
        api_thread = threading.Thread(target=run_api, daemon=True)
        api_thread.start()
        
        print("Waiting for API to start...")
        time.sleep(5)
        
        try:
            run_frontend()
        except KeyboardInterrupt:
            print("\nStopping both services...")
    
    elif choice == "4":
        print("Goodbye!")
    
    else:
        print("Invalid choice")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nLauncher stopped")
        sys.exit(0)