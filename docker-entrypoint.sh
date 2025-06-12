#!/bin/bash

# Docker entrypoint script for Jira Task Exporter
# Supports running API server, Web UI, or both services

set -e

# Function to start API server
start_api() {
    echo "🚀 Starting FastAPI server on port 8000..."
    python api_server.py --host 0.0.0.0 --port 8000 &
    API_PID=$!
    echo "API server started with PID: $API_PID"
}

# Function to start Web UI
start_web() {
    echo "🌐 Starting Streamlit Web UI on port 8501..."
    python -m streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true &
    WEB_PID=$!
    echo "Web UI started with PID: $WEB_PID"
}

# Function to wait for services
wait_for_services() {
    echo "✅ Services started successfully!"
    echo "📋 Jira Task Exporter is ready:"
    
    if [ ! -z "$API_PID" ]; then
        echo "   🔧 API Server: http://localhost:8000"
        echo "   📚 API Docs:   http://localhost:8000/docs"
    fi
    
    if [ ! -z "$WEB_PID" ]; then
        echo "   🌐 Web UI:     http://localhost:8501"
    fi
    
    echo ""
    echo "💡 Environment variables:"
    echo "   JIRA_API_TOKEN: ${JIRA_API_TOKEN:+***} ${JIRA_API_TOKEN:-Not set}"
    echo "   JIRA_API_URL:   ${JIRA_API_URL:-Not set}"
    echo "   JIRA_API_USER:  ${JIRA_API_USER:-Not set}"
    echo ""
    echo "🛑 Press Ctrl+C to stop all services"
    
    # Wait for any child process to exit
    wait
}

# Function to handle shutdown
shutdown() {
    echo ""
    echo "🛑 Shutting down services..."
    
    if [ ! -z "$API_PID" ]; then
        echo "Stopping API server (PID: $API_PID)..."
        kill $API_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$WEB_PID" ]; then
        echo "Stopping Web UI (PID: $WEB_PID)..."
        kill $WEB_PID 2>/dev/null || true
    fi
    
    echo "All services stopped."
    exit 0
}

# Set up signal handlers
trap shutdown SIGTERM SIGINT

# Main logic based on command argument
case "${1:-both}" in
    "api")
        echo "🔧 Starting API server only..."
        start_api
        wait $API_PID
        ;;
    "web")
        echo "🌐 Starting Web UI only..."
        start_web
        wait $WEB_PID
        ;;
    "both")
        echo "🚀 Starting both API server and Web UI..."
        start_api
        start_web
        wait_for_services
        ;;
    "cli")
        echo "🖥️  Starting CLI mode..."
        shift
        python jira_exporter.py "$@"
        ;;
    *)
        echo "Usage: $0 {api|web|both|cli}"
        echo ""
        echo "Services:"
        echo "  api  - Start only the FastAPI server (port 8000)"
        echo "  web  - Start only the Streamlit Web UI (port 8501)"
        echo "  both - Start both services (default)"
        echo "  cli  - Run CLI tool with provided arguments"
        echo ""
        echo "Examples:"
        echo "  docker run jira-exporter api"
        echo "  docker run jira-exporter web"
        echo "  docker run jira-exporter both"
        echo "  docker run jira-exporter cli SRD-1003 json"
        exit 1
        ;;
esac
