# Jira Task Exporter

[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub release](https://img.shields.io/github/release/kpapap/jira-tasks-export.svg)](https://github.com/kpapap/jira-tasks-export/releases)
[![GitHub issues](https://img.shields.io/github/issues/kpapap/jira-tasks-export.svg)](https://github.com/kpapap/jira-tasks-export/issues)

This script allows you to fetch Jira task data and export it in multiple formats: XML, JSON, Markdown, and Raw.

## Prerequisites

- Python 3.6 or higher
- Jira API token
- Jira server URL

## Installation

1. Create a virtual environment (optional but recommended):

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. (Optional) Set up environment variables by copying the example file:

```bash
cp .env.example .env
```

Then edit `.env` with your actual Jira credentials:

```bash
JIRA_API_TOKEN=your_jira_api_token_here
JIRA_API_USER=your_email@domain.com
JIRA_API_URL=your_domain.atlassian.net
```

## Usage

You can run the script in three ways:

### Method 1: Simplified Command (Recommended)

When you have a `.env` file configured, you can use the simplified syntax:

```bash
python jira_exporter.py <issue_key(s)> [format]
```

### Method 2: Command Line Arguments

```bash
python jira_exporter.py <jira_token> <jira_server> <issue_key(s)> [format]
```

### Method 3: Environment Variable Placeholders

```bash
python jira_exporter.py ":" "" <issue_key(s)> [format]
```

When using `":"` as the token and `""` as the server, the script will use the values from your `.env` file.

### Single Issue Export

```bash
# Simplified with .env file
python jira_exporter.py "SRD-1003" json

# Full command line arguments
python jira_exporter.py "your-token" "https://your-domain.atlassian.net" "PROJECT-123" json
```

### Multiple Issues Export

```bash
# Simplified with .env file
python jira_exporter.py "SRD-1003,SRD-1002,SV3-1" json

# Full command line arguments
python jira_exporter.py "your-token" "https://your-domain.atlassian.net" "PROJECT-123,PROJECT-124,PROJECT-125" json
```

The format parameter is optional and can be:

- xml (default): XML format
- json: JSON format
- markdown: Markdown format
- raw: Raw Jira API response

### Output Files

For single issues, the script creates: `<issue_key>_export.<extension>`

For multiple issues, the script creates separate files for each issue:

- `PROJECT-123_export.json`
- `PROJECT-124_export.json`
- `PROJECT-125_export.json`

The extension matches the chosen format:

- .xml for XML format
- .json for JSON format
- .md for Markdown format
- .txt for raw format

## Features

- Export in multiple formats: XML, JSON, Markdown, and raw Jira API response
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

## Output Formats

### XML

The XML output includes comprehensive issue data with structured fields:

- Basic information (key, summary, description)
- Status, priority, and dates
- People (assignee, reporter)
- Labels and components
- Comments with full history
- Web links
- Related issues (subtasks, epics, linked issues)

### JSON

Similar to XML but in JSON format, making it easy to parse and process programmatically.

### Markdown

The Markdown output is formatted with clear sections for:

- Issue title and key
- Issue details (type, status, priority)
- People (assignee, reporter)
- Dates (created, updated)
- Labels and components
- Description
- Comments with author and timestamp
- Related links
- Related issues grouped by relationship type (subtasks, epics, etc.)

## REST API

In addition to the command-line interface, the Jira Task Exporter also provides a REST API using FastAPI.

### Starting the API Server

```bash
# Start the API server
python start_api.py

# Or with custom host/port
python start_api.py --host 0.0.0.0 --port 8000

# For development with auto-reload
python start_api.py --reload
```

The API server will be available at:

- **API Server**: http://127.0.0.1:8000
- **Interactive API Documentation**: http://127.0.0.1:8000/docs
- **ReDoc Documentation**: http://127.0.0.1:8000/redoc

### API Endpoints

#### Export Issues (POST)

```bash
POST /export
Content-Type: application/json

{
  "issue_keys": ["SRD-1003", "SRD-1002"],
  "format": "json",
  "credentials": {
    "token": "your-api-token",
    "server": "your-domain.atlassian.net",
    "user": "your-email@domain.com"
  }
}
```

#### Export Single Issue (GET)

```bash
GET /export/SRD-1003?format=json&token=your-token&server=your-domain.atlassian.net
```

#### Export Multiple Issues (GET)

```bash
GET /export/multiple/SRD-1003,SRD-1002?format=markdown
```

#### Using Environment Variables

When `JIRA_API_TOKEN`, `JIRA_API_URL`, and `JIRA_API_USER` are configured:

```bash
POST /export
Content-Type: application/json

{
  "issue_keys": ["SRD-1003"],
  "format": "json"
}
```

### API Features

- **Multiple Export Formats**: XML, JSON, Markdown, Raw
- **Flexible Authentication**: Request credentials or environment variables
- **Single and Batch Export**: Export one or multiple issues
- **CORS Support**: Cross-origin requests enabled
- **Interactive Documentation**: Built-in Swagger UI and ReDoc
- **RESTful Design**: Standard HTTP methods and status codes
- **Error Handling**: Detailed error messages and appropriate HTTP codes

### API Examples

#### Using curl

```bash
# Export single issue
curl -X GET "http://localhost:8000/export/SRD-1003?format=json"

# Export multiple issues
curl -X POST "http://localhost:8000/export" \
  -H "Content-Type: application/json" \
  -d '{
    "issue_keys": ["SRD-1003", "SRD-1002"],
    "format": "markdown"
  }'
```

#### Using Python requests

```python
import requests

# Export single issue
response = requests.get("http://localhost:8000/export/SRD-1003?format=json")
data = response.json()

# Export multiple issues
response = requests.post("http://localhost:8000/export", json={
    "issue_keys": ["SRD-1003", "SRD-1002"],
    "format": "markdown"
})
result = response.json()
```
