#!/usr/bin/env python3
"""
Startup script for Streamlit Web UI.
"""

import subprocess
import sys
import argparse

def run_streamlit(port=8501, host="localhost"):
    """Run the Streamlit application."""
    cmd = [
        sys.executable, 
        "-m", 
        "streamlit", 
        "run", 
        "streamlit_app.py",
        "--server.port", str(port),
        "--server.address", host,
        "--server.headless", "true"
    ]
    
    print(f"🚀 Starting Streamlit Web UI on http://{host}:{port}")
    print("📋 Jira Task Exporter - Web Interface")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Streamlit server...")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start Jira Task Exporter Web UI")
    parser.add_argument("--port", type=int, default=8501, help="Port to run on (default: 8501)")
    parser.add_argument("--host", default="localhost", help="Host to bind to (default: localhost)")
    
    args = parser.parse_args()
    run_streamlit(port=args.port, host=args.host)
