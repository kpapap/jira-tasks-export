#!/usr/bin/env python3
"""
Streamlit Web UI for Jira Task Exporter.
Provides a user-friendly web interface for exporting Jira tasks.
"""

import streamlit as st
import os
import json
import tempfile
import zipfile
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv
import io

from jira_exporter import JiraExporter

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="Jira Task Exporter",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    .export-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables."""
    if 'export_results' not in st.session_state:
        st.session_state.export_results = {}
    if 'last_export_time' not in st.session_state:
        st.session_state.last_export_time = None

def validate_credentials(token: str, server: str, user: str = None) -> bool:
    """Validate Jira credentials."""
    try:
        if not token or not server:
            return False
        
        # Build authentication token
        auth_token = token
        if user and ':' not in token:
            auth_token = f"{user}:{token}"
        
        # Test connection
        exporter = JiraExporter(auth_token, server)
        # Try to access Jira (this will fail if credentials are invalid)
        return True
    except Exception:
        return False

def get_credentials_from_env() -> tuple:
    """Get credentials from environment variables."""
    token = os.getenv('JIRA_API_TOKEN')
    server = os.getenv('JIRA_API_URL')
    user = os.getenv('JIRA_API_USER')
    return token, server, user

def export_issues(issue_keys: List[str], format_type: str, token: str, server: str, user: str = None) -> Dict:
    """Export Jira issues."""
    try:
        # Build authentication token
        auth_token = token
        if user and ':' not in token:
            auth_token = f"{user}:{token}"
        
        # Initialize exporter
        exporter = JiraExporter(auth_token, server)
        
        # Export issues
        results = {}
        errors = []
        
        for issue_key in issue_keys:
            try:
                content = exporter.get_issue(issue_key, format_type)
                if content:
                    results[issue_key] = content
                else:
                    errors.append(f"Failed to export {issue_key}")
            except Exception as e:
                errors.append(f"Error exporting {issue_key}: {str(e)}")
        
        return {
            'success': len(results) > 0,
            'results': results,
            'errors': errors,
            'format': format_type
        }
    except Exception as e:
        return {
            'success': False,
            'results': {},
            'errors': [f"Export failed: {str(e)}"],
            'format': format_type
        }

def create_download_content(results: Dict, format_type: str) -> bytes:
    """Create downloadable content for export results."""
    if len(results) == 1:
        # Single file
        issue_key = list(results.keys())[0]
        content = results[issue_key]
        if isinstance(content, dict):
            content = json.dumps(content, indent=2)
        return content.encode('utf-8')
    else:
        # Multiple files in a ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for issue_key, content in results.items():
                ext = {
                    'xml': 'xml',
                    'json': 'json', 
                    'markdown': 'md',
                    'raw': 'txt'
                }.get(format_type, 'txt')
                
                filename = f"{issue_key}_export.{ext}"
                
                if isinstance(content, dict):
                    content = json.dumps(content, indent=2)
                
                zip_file.writestr(filename, content)
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()

def main():
    """Main Streamlit application."""
    init_session_state()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📋 Jira Task Exporter</h1>
        <p>Export Jira tasks in multiple formats: XML, JSON, Markdown, and Raw</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Check for environment variables
        env_token, env_server, env_user = get_credentials_from_env()
        has_env_config = bool(env_token and env_server)
        
        if has_env_config:
            st.success("✅ Environment variables detected")
            st.info(f"Server: {env_server}")
            if env_user:
                st.info(f"User: {env_user}")
        
        # Credential input method
        use_env = st.checkbox(
            "Use environment variables", 
            value=has_env_config,
            disabled=not has_env_config,
            help="Use credentials from .env file"
        )
        
        if not use_env or not has_env_config:
            st.subheader("Jira Credentials")
            
            server = st.text_input(
                "Jira Server URL",
                placeholder="your-domain.atlassian.net",
                help="Your Jira server URL (without https://)"
            )
            
            user = st.text_input(
                "Email Address",
                placeholder="your-email@domain.com",
                help="Your Jira account email"
            )
            
            token = st.text_input(
                "API Token",
                type="password",
                placeholder="Your Jira API token",
                help="Generate from: https://id.atlassian.com/manage-profile/security/api-tokens"
            )
        else:
            server = env_server
            user = env_user
            token = env_token
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📤 Export Issues")
        
        # Issue input
        st.subheader("Issue Keys")
        issue_input_method = st.radio(
            "Input method:",
            ["Single issue", "Multiple issues (comma-separated)", "Text area (one per line)"],
            horizontal=True
        )
        
        issue_keys = []
        
        if issue_input_method == "Single issue":
            single_issue = st.text_input(
                "Issue Key",
                placeholder="e.g., PROJECT-123",
                help="Enter a single Jira issue key"
            )
            if single_issue:
                issue_keys = [single_issue.strip()]
                
        elif issue_input_method == "Multiple issues (comma-separated)":
            multiple_issues = st.text_input(
                "Issue Keys",
                placeholder="e.g., PROJECT-123, PROJECT-124, PROJECT-125",
                help="Enter multiple issue keys separated by commas"
            )
            if multiple_issues:
                issue_keys = [key.strip() for key in multiple_issues.split(',') if key.strip()]
                
        else:  # Text area
            issues_text = st.text_area(
                "Issue Keys",
                placeholder="PROJECT-123\nPROJECT-124\nPROJECT-125",
                help="Enter one issue key per line",
                height=100
            )
            if issues_text:
                issue_keys = [key.strip() for key in issues_text.split('\n') if key.strip()]
        
        # Format selection
        st.subheader("Export Format")
        format_type = st.selectbox(
            "Choose format:",
            ["json", "xml", "markdown", "raw"],
            help="Select the export format for the issues"
        )
        
        # Format descriptions
        format_descriptions = {
            "json": "JSON format - Easy to parse programmatically",
            "xml": "XML format - Structured data with tags",
            "markdown": "Markdown format - Human-readable documentation",
            "raw": "Raw format - Direct Jira API response"
        }
        st.info(f"📝 {format_descriptions[format_type]}")
        
        # Export button
        if st.button("🚀 Export Issues", type="primary", use_container_width=True):
            if not issue_keys:
                st.error("❌ Please enter at least one issue key")
            elif not token or not server:
                st.error("❌ Please provide Jira credentials")
            else:
                # Validate credentials
                with st.spinner("Validating credentials..."):
                    if not validate_credentials(token, server, user):
                        st.error("❌ Invalid Jira credentials. Please check your token and server URL.")
                    else:
                        # Export issues
                        with st.spinner(f"Exporting {len(issue_keys)} issue(s)..."):
                            export_result = export_issues(issue_keys, format_type, token, server, user)
                            st.session_state.export_results = export_result
                            st.session_state.last_export_time = datetime.now()
                            
                            if export_result['success']:
                                st.success(f"✅ Successfully exported {len(export_result['results'])} issue(s)")
                            else:
                                st.error("❌ Export failed")
    
    with col2:
        st.header("📊 Export Status")
        
        if st.session_state.export_results:
            results = st.session_state.export_results
            
            # Summary
            st.metric(
                "Issues Exported",
                len(results['results']),
                delta=len(results['results']) if results['success'] else -len(issue_keys) if 'issue_keys' in locals() else 0
            )
            
            if st.session_state.last_export_time:
                st.write(f"⏰ Last export: {st.session_state.last_export_time.strftime('%H:%M:%S')}")
            
            # Show errors if any
            if results['errors']:
                st.subheader("⚠️ Errors")
                for error in results['errors']:
                    st.error(error)
            
            # Show successful exports
            if results['results']:
                st.subheader("✅ Exported Issues")
                for issue_key in results['results'].keys():
                    st.write(f"• {issue_key}")
        else:
            st.info("No exports yet. Configure your credentials and export some issues!")
    
    # Download section
    if st.session_state.export_results and st.session_state.export_results['success']:
        st.header("💾 Download Results")
        
        results = st.session_state.export_results
        
        # Create download content
        download_content = create_download_content(results['results'], results['format'])
        
        # Determine filename and mimetype
        if len(results['results']) == 1:
            issue_key = list(results['results'].keys())[0]
            ext = {
                'xml': 'xml',
                'json': 'json',
                'markdown': 'md',
                'raw': 'txt'
            }.get(results['format'], 'txt')
            filename = f"{issue_key}_export.{ext}"
            mimetype = {
                'xml': 'application/xml',
                'json': 'application/json',
                'markdown': 'text/markdown',
                'raw': 'text/plain'
            }.get(results['format'], 'text/plain')
        else:
            filename = f"jira_exports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            mimetype = 'application/zip'
        
        # Download button
        st.download_button(
            label=f"📥 Download {filename}",
            data=download_content,
            file_name=filename,
            mime=mimetype,
            use_container_width=True
        )
        
        # Preview section
        st.header("👀 Preview")
        
        if len(results['results']) == 1:
            issue_key = list(results['results'].keys())[0]
            content = results['results'][issue_key]
            
            if results['format'] == 'json':
                if isinstance(content, dict):
                    st.json(content)
                else:
                    try:
                        st.json(json.loads(content))
                    except:
                        st.text(content)
            elif results['format'] == 'markdown':
                st.markdown(content)
            else:
                st.text(content)
        else:
            st.info(f"📦 {len(results['results'])} files ready for download as ZIP archive")
            
            # Show file list
            for issue_key in results['results'].keys():
                ext = {
                    'xml': 'xml',
                    'json': 'json',
                    'markdown': 'md',
                    'raw': 'txt'
                }.get(results['format'], 'txt')
                st.write(f"• {issue_key}_export.{ext}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>🛠️ Jira Task Exporter v1.2.0 | Built with Streamlit</p>
        <p>💡 Also available as CLI tool and REST API</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
