# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [Unreleased]

## [1.3.0] - 2025-06-12

### Added

- **Streamlit Web UI**: Complete web interface for non-technical users
  - User-friendly graphical interface with modern styling
  - Multiple input methods (single issue, comma-separated, text area)
  - Real-time export status and progress tracking
  - Instant download functionality with ZIP support for multiple files
  - Content preview for exported data
  - Automatic environment variable detection
  - Secure credential handling with session isolation
- **Web Interface Features**:
  - Clean, responsive design with custom CSS styling
  - Visual progress indicators and status updates
  - One-click downloads for single files or ZIP archives
  - Browser-based content preview
  - Batch processing with automatic file organization
- **Startup Script**: `start_web.py` for easy web server launch
- **Enhanced Documentation**: Updated README.md with comprehensive Web UI section

### Technical Details

- Added Streamlit>=1.28.0 dependency
- Web UI runs on `http://localhost:8501` by default
- Supports all existing export formats and features
- Perfect for non-technical users who prefer graphical interfaces
- Complements existing CLI and REST API interfaces

## [1.2.0] - 2025-06-12

### Added

- **FastAPI REST API Server**: Complete REST API interface for all CLI functionality
  - Multiple API endpoints for single and batch exports
  - Support for all export formats (XML, JSON, Markdown, Raw)
  - Environment variable and explicit credential support
  - Comprehensive API documentation with Swagger UI at `/docs`
  - CORS middleware for web application compatibility
  - Proper error handling and response models
- **API Endpoints**:
  - `POST /export` - Batch export with request body
  - `GET /export/{issue_key}` - Single issue export via URL path
  - `GET /export/multiple/{issue_keys}` - Multiple issues via URL path
  - `GET /health` - Health check endpoint
  - `GET /formats` - List supported export formats
  - `GET /docs-examples` - API usage examples
- **Server Management**:
  - `start_api.py` - Easy server startup script
  - Command-line arguments for host, port, and reload options
  - Background process support for development
- **Dependencies**: Added FastAPI and Uvicorn to requirements.txt

### Technical Details

- The API server runs on `http://localhost:8000` by default
- Interactive documentation available at `/docs` and `/redoc`
- Supports both environment variables and explicit credentials in requests
- All CLI functionality is now accessible via REST API
- CORS enabled for cross-origin requests from web applications

## [1.1.0] - 2025-06-12

### Added

- Environment variable support for Jira credentials
- Simplified command syntax: `python jira_exporter.py ISSUE-KEY format`
- Automatic detection of `.env` file configuration
- Support for `python-dotenv` package
- Enhanced help messages with multiple usage examples

### Changed

- Command line interface now supports simplified syntax when `.env` is configured
- Updated README.md with comprehensive usage examples
- Improved error handling for missing environment variables

### Maintained

- Full backward compatibility with original command syntax
- Support for environment variable placeholders (`:` and `""`)

## [1.0.0] - 2025-06-12

### Added

- Initial release of Jira Task Exporter
- Support for multiple export formats: XML, JSON, Markdown, and Raw
- Comprehensive issue data export including:
  - Basic fields (key, summary, description, etc.)
  - Status, priority, and dates
  - Assignee and reporter information
  - Labels and components
  - Comments with author and timestamps
  - Web links with relationships
- Rich relationship support:
  - Direct subtasks
  - Epic/Story relationships
  - Issue links (both inward and outward)
  - Relationship type preservation
- Support for single and multiple issue exports
- Command-line interface with flexible parameters
- Proper error handling and validation
- Comprehensive documentation

### Dependencies

- requests>=2.31.0
- jira>=3.5.1
- xmltodict>=0.13.0
- markdown>=3.4.3
- python-dotenv>=1.0.0

[Unreleased]: https://github.com/kpapap/jira-tasks-export/compare/v1.1.0...HEAD
[1.3.0]: https://github.com/kpapap/jira-tasks-export/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/kpapap/jira-tasks-export/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/kpapap/jira-tasks-export/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/kpapap/jira-tasks-export/releases/tag/v1.0.0
