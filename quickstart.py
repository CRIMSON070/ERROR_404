"""
Quick Start Script for IPL Auction Platform
Automatically trains models and starts servers
"""

import os
import sys
import subprocess
import time


def print_banner(text):
    """Print formatted banner"""
    print("\n" + "="*60)
    print(f" {text}")
    print("="*60 + "\n")


def check_requirements():
    """Check if required packages are installed"""
    
    print_banner("Checking Requirements")
    
    required = ['streamlit', 'fastapi', 'uvicorn', 'torch', 'pandas', 'numpy']
    missing = []
    
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing packages: {missing}")
        print("\nInstall with:")
        print("  pip install -r requirements.txt")
        return False
    
    print("\n✅ All requirements satisfied!")
    return True


def train_models():
    """Train all DL models"""
    
    print_banner("Step 1: Training Deep Learning Models")
    
    try:
        from models.train_all_models import main as train_main
        
        report = train_main()
        
        success_rate = report.get('success_rate', 0)
        
        if success_rate >= 80:
            print("\n✅ Models trained successfully!")
            return True
        else:
            print(f"\n⚠️  Some models failed ({success_rate:.1f}% success)")
            return True  # Continue anyway
    
    except Exception as e:
        print(f"\n⚠️  Model training failed: {e}")
        print("Continuing with synthetic data...")
        return True


def start_backend():
    """Start FastAPI backend"""
    
    print_banner("Step 2: Starting FastAPI Backend")
    
    try:
        # Start backend in background
        backend_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
            cwd="backend",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print("⏳ Waiting for backend to start (10 seconds)...")
        time.sleep(10)
        
        # Check if backend is running
        import requests
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            
            if response.status_code == 200:
                print("✅ Backend started successfully!")
                print("📍 API available at: http://localhost:8000")
                print("📍 API docs at: http://localhost:8000/docs")
                return backend_process
        except:
            print("⚠️  Backend may not have started properly")
            return backend_process
    
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None


def start_frontend():
    """Start Streamlit frontend"""
    
    print_banner("Step 3: Starting Streamlit Frontend")
    
    try:
        # Start frontend
        frontend_process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "frontend/app.py"],
            cwd="frontend"
        )
        
        print("✅ Frontend started!")
        print("📍 Open your browser to: http://localhost:8501")
        
        return frontend_process
    
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None


def main():
    """Main startup sequence"""
    
    print("\n" + "="*60)
    print(" 🏏 IPL AUCTION STRATEGY PLATFORM - QUICK START")
    print("="*60)
    
    # Check requirements
    if not check_requirements():
        print("\nPlease install dependencies first:")
        print("  pip install -r requirements.txt")
        return
    
    # Ask about model training
    print("\n" + "="*60)
    choice = input("\nTrain Deep Learning models now? (y/n): ").lower().strip()
    
    if choice == 'y':
        train_models()
    else:
        print("⚠️  Skipping model training - using synthetic data")
    
    # Start servers
    backend_process = start_backend()
    
    if backend_process:
        time.sleep(2)
        frontend_process = start_frontend()
        
        print_banner("Platform Running!")
        print("✅ Backend:  http://localhost:8000")
        print("✅ Frontend: http://localhost:8501")
        print("\n📊 API Documentation: http://localhost:8000/docs")
        print("\nPress Ctrl+C in both terminals to stop the servers")
        
        # Keep running
        try:
            if frontend_process:
                frontend_process.wait()
            if backend_process:
                backend_process.wait()
        except KeyboardInterrupt:
            print("\n\n👋 Shutting down...")
            if backend_process:
                backend_process.terminate()
            if frontend_process:
                frontend_process.terminate()


if __name__ == "__main__":
    main()
