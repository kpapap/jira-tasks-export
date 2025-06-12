#!/usr/bin/env python3
"""
Script to start the Jira Task Exporter API server.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api_server import run_server

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Start Jira Task Exporter API Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--public", action="store_true", help="Bind to all interfaces (0.0.0.0)")
    
    args = parser.parse_args()
    
    host = "0.0.0.0" if args.public else args.host
    
    print("🚀 Starting Jira Task Exporter API Server")
    print(f"📍 Server: http://{host}:{args.port}")
    print(f"📖 API Docs: http://{host}:{args.port}/docs")
    print(f"📚 ReDoc: http://{host}:{args.port}/redoc")
    print("⏹️  Press Ctrl+C to stop")
    print()
    
    try:
        run_server(host=host, port=args.port, reload=args.reload)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
