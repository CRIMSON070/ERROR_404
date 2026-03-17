"""
Launcher script to run the FastAPI backend with proper paths
"""
import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'backend'))
sys.path.insert(0, os.path.join(project_root, 'models'))
sys.path.insert(0, os.path.join(project_root, 'spark_jobs'))

# Set environment variables
os.environ['PYTHONPATH'] = project_root

print(f"🚀 Starting IPL Auction Strategy Platform Backend")
print(f"📍 Project Root: {project_root}")
print(f"🔧 Python Path: {sys.path[:3]}")

# Import and run uvicorn
import uvicorn

if __name__ == "__main__":
    print("\n✅ Loading models and data...")
    
    # Start server
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
