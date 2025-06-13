#!/usr/bin/env python3
import subprocess
import sys
import time
import os
import threading
from dotenv import load_dotenv
from pymongo import MongoClient

def check_environment():
    print("Checking Environment...")
    
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY not found!")
        print("Please create a .env file with:")
        print("OPENAI_API_KEY=your_openai_api_key_here")
        return False
    
    print("OpenAI API key found")
    
    try:
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
        client.server_info()
        print("MongoDB connection successful")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        print("Please ensure MongoDB is running on localhost:27017")
        return False
    
    pdf_path = '/Users/omkarsatapaphy/Downloads/Apple Laptop FAQ.pdf'
    if not os.path.exists(pdf_path):
        print(f"FAQ PDF not found at: {pdf_path}")
        print("Please update the path in tools.py")
    else:
        print("FAQ PDF found")
    
    return True

def run_api():
    try:
        print("Starting Flask API...")
        subprocess.run([sys.executable, "api.py"])
    except KeyboardInterrupt:
        print("API stopped")

def run_frontend():
    try:
        print("Starting Streamlit frontend...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py", "--server.port=8501"])
    except KeyboardInterrupt:
        print("Frontend stopped")

def main():
    print("Lumi AI Assistant")
    print("=" * 30)
    
    if not check_environment():
        return
    
    print("\nStarting both services...")
    print("API: http://localhost:5001")
    print("Frontend: http://localhost:8501")
    print("Press Ctrl+C to stop")
    
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    
    print("Waiting for API to start...")
    time.sleep(5)
    
    try:
        run_frontend()
    except KeyboardInterrupt:
        print("\nStopping services...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nLauncher stopped")
        sys.exit(0)