#!/usr/bin/env python3
"""
FastAPI REST API server for Jira Task Exporter.
Provides web API interface for all CLI functionality.
"""

import os
import logging
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Path, Body, Depends
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import uvicorn

from jira_exporter import JiraExporter

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Jira Task Exporter API",
    description="REST API for exporting Jira tasks in multiple formats (XML, JSON, Markdown, Raw)",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class JiraCredentials(BaseModel):
    """Jira authentication credentials."""
    token: str = Field(..., description="Jira API token or email:token combination")
    server: str = Field(..., description="Jira server URL")
    user: Optional[str] = Field(None, description="Jira user email (if not included in token)")

class ExportRequest(BaseModel):
    """Request model for exporting issues."""
    issue_keys: List[str] = Field(..., description="List of Jira issue keys to export")
    format: str = Field("json", description="Export format: xml, json, markdown, raw")
    credentials: Optional[JiraCredentials] = Field(None, description="Jira credentials (optional if using env vars)")

class ExportResponse(BaseModel):
    """Response model for export operations."""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Status message")
    data: Optional[Dict[str, Any]] = Field(None, description="Exported data")
    errors: Optional[List[str]] = Field(None, description="Any errors that occurred")

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")

# Dependency to get Jira credentials
async def get_jira_credentials(credentials: Optional[JiraCredentials] = None) -> tuple:
    """Get Jira credentials from request or environment variables."""
    if credentials:
        # Use provided credentials
        token = credentials.token
        server = credentials.server
        if credentials.user and ':' not in token:
            token = f"{credentials.user}:{token}"
    else:
        # Use environment variables
        token = os.getenv('JIRA_API_TOKEN')
        server = os.getenv('JIRA_API_URL')
        user = os.getenv('JIRA_API_USER')
        
        if not token or not server:
            raise HTTPException(
                status_code=400,
                detail="Jira credentials not provided. Either pass credentials in request or set environment variables (JIRA_API_TOKEN, JIRA_API_URL, JIRA_API_USER)"
            )
        
        if user and ':' not in token:
            token = f"{user}:{token}"
    
    return token, server

# API Routes

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - API health check."""
    return HealthResponse(
        status="healthy",
        version="1.1.0"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.1.0"
    )

@app.post("/export", response_model=ExportResponse)
async def export_issues(request: ExportRequest):
    """
    Export Jira issues in the specified format.
    
    - **issue_keys**: List of Jira issue keys (e.g., ["PROJECT-123", "PROJECT-124"])
    - **format**: Export format (xml, json, markdown, raw)
    - **credentials**: Optional Jira credentials (uses env vars if not provided)
    """
    try:
        # Validate format
        if request.format not in ['xml', 'json', 'markdown', 'raw']:
            raise HTTPException(
                status_code=400,
                detail="Invalid format. Must be one of: xml, json, markdown, raw"
            )
        
        # Get credentials
        token, server = await get_jira_credentials(request.credentials)
        
        # Initialize exporter
        exporter = JiraExporter(token, server)
        
        # Export issues
        if len(request.issue_keys) == 1:
            # Single issue
            content = exporter.get_issue(request.issue_keys[0], request.format)
            if content:
                data = {request.issue_keys[0]: content}
                message = f"Successfully exported {request.issue_keys[0]} in {request.format} format"
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"Failed to export issue {request.issue_keys[0]}"
                )
        else:
            # Multiple issues
            results = exporter.get_multiple_issues(request.issue_keys, request.format)
            data = results
            success_count = sum(1 for v in results.values() if v is not None)
            message = f"Successfully exported {success_count} out of {len(request.issue_keys)} issues in {request.format} format"
            
            if success_count == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Failed to export any issues"
                )
        
        return ExportResponse(
            success=True,
            message=message,
            data=data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting issues: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/export/{issue_key}")
async def export_single_issue(
    issue_key: str,
    format: str = Query("json", description="Export format: xml, json, markdown, raw"),
    token: Optional[str] = Query(None, description="Jira API token"),
    server: Optional[str] = Query(None, description="Jira server URL"),
    user: Optional[str] = Query(None, description="Jira user email")
):
    """
    Export a single Jira issue using query parameters.
    
    - **issue_key**: Jira issue key (e.g., "PROJECT-123")
    - **format**: Export format (xml, json, markdown, raw)
    - **token**: Optional Jira API token (uses env var if not provided)
    - **server**: Optional Jira server URL (uses env var if not provided)
    - **user**: Optional Jira user email (uses env var if not provided)
    """
    try:
        # Validate format
        if format not in ['xml', 'json', 'markdown', 'raw']:
            raise HTTPException(
                status_code=400,
                detail="Invalid format. Must be one of: xml, json, markdown, raw"
            )
        
        # Build credentials
        credentials = None
        if token and server:
            credentials = JiraCredentials(token=token, server=server, user=user)
        
        # Get credentials
        auth_token, auth_server = await get_jira_credentials(credentials)
        
        # Initialize exporter
        exporter = JiraExporter(auth_token, auth_server)
        
        # Export issue
        content = exporter.get_issue(issue_key, format)
        
        if not content:
            raise HTTPException(
                status_code=404,
                detail=f"Issue {issue_key} not found or could not be exported"
            )
        
        # Return appropriate response type based on format
        if format == 'xml':
            return PlainTextResponse(content, media_type="application/xml")
        elif format == 'json':
            return JSONResponse(content=eval(content) if isinstance(content, str) else content)
        elif format in ['markdown', 'raw']:
            return PlainTextResponse(content, media_type="text/plain")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting issue {issue_key}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/export/multiple/{issue_keys}")
async def export_multiple_issues_get(
    issue_keys: str,
    format: str = Query("json", description="Export format: xml, json, markdown, raw"),
    token: Optional[str] = Query(None, description="Jira API token"),
    server: Optional[str] = Query(None, description="Jira server URL"),
    user: Optional[str] = Query(None, description="Jira user email")
):
    """
    Export multiple Jira issues using GET with query parameters.
    
    - **issue_keys**: Comma-separated list of issue keys (e.g., "PROJECT-123,PROJECT-124")
    - **format**: Export format (xml, json, markdown, raw)
    - **token**: Optional Jira API token (uses env var if not provided)
    - **server**: Optional Jira server URL (uses env var if not provided)
    - **user**: Optional Jira user email (uses env var if not provided)
    """
    # Parse issue keys
    keys_list = [key.strip() for key in issue_keys.split(',')]
    
    # Build request
    credentials = None
    if token and server:
        credentials = JiraCredentials(token=token, server=server, user=user)
    
    request = ExportRequest(
        issue_keys=keys_list,
        format=format,
        credentials=credentials
    )
    
    # Use the existing export endpoint
    return await export_issues(request)

@app.get("/formats")
async def get_supported_formats():
    """Get list of supported export formats."""
    return {
        "formats": [
            {
                "name": "xml",
                "description": "XML format with structured data",
                "media_type": "application/xml"
            },
            {
                "name": "json", 
                "description": "JSON format for programmatic use",
                "media_type": "application/json"
            },
            {
                "name": "markdown",
                "description": "Markdown format for documentation",
                "media_type": "text/markdown"
            },
            {
                "name": "raw",
                "description": "Raw Jira API response",
                "media_type": "text/plain"
            }
        ]
    }

@app.get("/docs-examples")
async def get_api_examples():
    """Get API usage examples."""
    return {
        "examples": {
            "single_issue_post": {
                "method": "POST",
                "url": "/export",
                "body": {
                    "issue_keys": ["PROJECT-123"],
                    "format": "json",
                    "credentials": {
                        "token": "your-api-token",
                        "server": "your-domain.atlassian.net",
                        "user": "your-email@domain.com"
                    }
                }
            },
            "single_issue_get": {
                "method": "GET", 
                "url": "/export/PROJECT-123?format=json&token=your-token&server=your-domain.atlassian.net"
            },
            "multiple_issues_post": {
                "method": "POST",
                "url": "/export",
                "body": {
                    "issue_keys": ["PROJECT-123", "PROJECT-124"],
                    "format": "markdown"
                }
            },
            "multiple_issues_get": {
                "method": "GET",
                "url": "/export/multiple/PROJECT-123,PROJECT-124?format=xml"
            },
            "using_env_vars": {
                "description": "When JIRA_API_TOKEN, JIRA_API_URL, and JIRA_API_USER are set as environment variables",
                "method": "POST",
                "url": "/export", 
                "body": {
                    "issue_keys": ["PROJECT-123"],
                    "format": "json"
                }
            }
        }
    }

# Development server function
def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the FastAPI server."""
    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Jira Task Exporter API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to") 
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    
    args = parser.parse_args()
    
    print(f"Starting Jira Task Exporter API Server on {args.host}:{args.port}")
    print(f"API Documentation available at: http://{args.host}:{args.port}/docs")
    print(f"ReDoc Documentation available at: http://{args.host}:{args.port}/redoc")
    
    run_server(host=args.host, port=args.port, reload=args.reload)
