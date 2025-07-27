"""
Simple script to run the TinyGPT-MCP backend server
"""
import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def run_server():
    """Run the FastAPI server"""
    print("Starting TinyGPT-MCP backend server...")
    print("Server will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == "__main__":
    # Check if we're in the backend directory
    if not os.path.exists("requirements.txt"):
        print("Error: Please run this script from the backend directory")
        sys.exit(1)
    
    # Install requirements if needed
    try:
        import fastapi
        import uvicorn
    except ImportError:
        install_requirements()
    
    # Run the server
    run_server()