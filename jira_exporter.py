#!/usr/bin/env python3

import os
import sys
import logging
from typing import Optional
from jira import JIRA
from jira.exceptions import JIRAError
from exporters import JiraExporters

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class JiraExporter:
    def __init__(self, token: str, server: str):
        """Initialize Jira client with authentication token."""
        # Ensure server URL is properly formatted
        self.server = server.rstrip('/')
        if not self.server.startswith(('http://', 'https://')):
            self.server = f'https://{self.server}'
            
        # Clean up token (remove any whitespace)
        self.token = token.strip()
        self.jira = None
        self.exporters = None
        self._connect()

    def _connect(self) -> None:
        """Establish connection to Jira."""
        try:
            # Extract email from token if it's in the format "email:token"
            if ':' in self.token:
                email, api_token = self.token.split(':', 1)
            else:
                # If no email provided, check environment variable
                email = os.getenv('JIRA_EMAIL')
                if not email:
                    raise ValueError("Email is required. Either provide it as 'email:token' or set JIRA_EMAIL environment variable")
                api_token = self.token

            # Log connection attempt (without exposing the full token)
            token_preview = f"{api_token[:5]}...{api_token[-5:]}"
            logger.info(f"Attempting to connect to {self.server} with user {email}")
            
            self.jira = JIRA(
                server=self.server,
                basic_auth=(email, api_token)  # Use basic auth with email and token
            )
            logger.info("Successfully connected to Jira")
            
            # Initialize the exporters with the Jira client after connection is established
            self.exporters = JiraExporters(self.jira)
            
        except JIRAError as e:
            if e.status_code == 403:
                logger.error("Authentication failed. Please check your email and API token are valid.")
                logger.error("Format should be: 'your-email@domain.com:your-api-token'")
            logger.error(f"Failed to connect to Jira: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while connecting to Jira: {str(e)}")
            raise

    def get_issue(self, issue_key: str, format: str = 'xml') -> Optional[str]:
        """
        Fetch issue data and convert to the specified format.
        
        Args:
            issue_key: The Jira issue key (e.g., 'PROJECT-123')
            format: Export format ('xml', 'json', 'markdown', 'raw')
            
        Returns:
            String containing issue data in the specified format
        """
        try:
            issue = self.jira.issue(issue_key)
            logger.info(f"Successfully fetched issue {issue_key}")
            
            # Get subtasks data once for all formats
            subtasks_data = self._get_subtasks(issue)
            
            if format == 'xml':
                return self.exporters.to_xml(issue, subtasks_data)
            elif format == 'json':
                return self.exporters.to_json(issue, subtasks_data)
            elif format == 'markdown':
                json_content = self.exporters.to_json(issue, subtasks_data)
                if json_content:
                    return self.exporters.json_to_markdown(json_content)
                return None
            elif format == 'raw':
                return str(issue.raw)
            else:
                logger.error(f"Unsupported format: {format}")
                return None
            
        except JIRAError as e:
            logger.error(f"Failed to fetch issue {issue_key}: {str(e)}")
            return None

    def get_multiple_issues(self, issue_keys: list, format: str = 'xml') -> dict:
        """
        Fetch multiple issues and convert to the specified format.
        
        Args:
            issue_keys: List of Jira issue keys (e.g., ['PROJECT-123', 'PROJECT-124'])
            format: Export format ('xml', 'json', 'markdown', 'raw')
            
        Returns:
            Dictionary with issue_key as key and exported content as value
        """
        results = {}
        
        for issue_key in issue_keys:
            logger.info(f"Processing issue {issue_key}")
            content = self.get_issue(issue_key, format)
            if content:
                results[issue_key] = content
            else:
                logger.warning(f"Failed to export issue {issue_key}")
                results[issue_key] = None
                
        return results

    def _get_subtasks(self, issue) -> list:
        """Fetch subtasks, epic issues, and other linked issues with detailed information."""
        related_issues = []
        
        # Get direct subtasks
        if hasattr(issue.fields, 'subtasks') and issue.fields.subtasks:
            for subtask in issue.fields.subtasks:
                # Fetch the full subtask to get all fields
                full_subtask = self.jira.issue(subtask.key)
                related_issues.append({
                    'key': full_subtask.key,
                    'summary': full_subtask.fields.summary,
                    'status': full_subtask.fields.status.name,
                    'assignee': full_subtask.fields.assignee.displayName if full_subtask.fields.assignee else 'Unassigned',
                    'type': full_subtask.fields.issuetype.name,
                    'priority': full_subtask.fields.priority.name if full_subtask.fields.priority else 'None',
                    'created': full_subtask.fields.created,
                    'updated': full_subtask.fields.updated,
                    'relationship': 'subtask',
                    'description': full_subtask.fields.description or '',
                    'components': [c.name for c in full_subtask.fields.components] if full_subtask.fields.components else [],
                    'labels': full_subtask.fields.labels if full_subtask.fields.labels else []
                })
    
        # Get epic issues if this is an epic
        if hasattr(issue.fields, 'issuetype') and issue.fields.issuetype.name.lower() == 'epic':
            try:
                # Get issues in epic - this requires the JIRA Agile API
                epic_issues = self.jira.search_issues(f'parent = {issue.key} OR "Epic Link" = {issue.key}')
                for epic_issue in epic_issues:
                    # Get full issue details
                    full_issue = self.jira.issue(epic_issue.key)
                    related_issues.append({
                        'key': full_issue.key,
                        'summary': full_issue.fields.summary,
                        'status': full_issue.fields.status.name,
                        'assignee': full_issue.fields.assignee.displayName if full_issue.fields.assignee else 'Unassigned',
                        'type': full_issue.fields.issuetype.name,
                        'priority': full_issue.fields.priority.name if full_issue.fields.priority else 'None',
                        'created': full_issue.fields.created,
                        'updated': full_issue.fields.updated,
                        'relationship': 'epic',
                        'description': full_issue.fields.description or '',
                        'components': [c.name for c in full_issue.fields.components] if full_issue.fields.components else [],
                        'labels': full_issue.fields.labels if full_issue.fields.labels else []
                    })
            except Exception as e:
                logger.warning(f"Failed to fetch epic issues for {issue.key}: {str(e)}")
    
        # Get linked issues (keeping existing linked issues functionality)
        if hasattr(issue.fields, 'issuelinks') and issue.fields.issuelinks:
            for link in issue.fields.issuelinks:
                # Determine the linked issue and relationship type
                if hasattr(link, 'outwardIssue'):
                    linked_issue = link.outwardIssue
                    relationship = link.type.outward
                elif hasattr(link, 'inwardIssue'):
                    linked_issue = link.inwardIssue
                    relationship = link.type.inward
                else:
                    continue
                
                # Fetch full linked issue
                full_linked = self.jira.issue(linked_issue.key)
                related_issues.append({
                    'key': full_linked.key,
                    'summary': full_linked.fields.summary,
                    'status': full_linked.fields.status.name,
                    'assignee': full_linked.fields.assignee.displayName if full_linked.fields.assignee else 'Unassigned',
                    'type': full_linked.fields.issuetype.name,
                    'priority': full_linked.fields.priority.name if full_linked.fields.priority else 'None',
                    'created': full_linked.fields.created,
                    'updated': full_linked.fields.updated,
                    'relationship': relationship,
                    'description': full_linked.fields.description or '',
                    'components': [c.name for c in full_linked.fields.components] if full_linked.fields.components else [],
                    'labels': full_linked.fields.labels if full_linked.fields.labels else []
                })
            
        return related_issues

def main():
    if len(sys.argv) < 4:
        print("Usage: python jira_exporter.py <jira_token> <jira_server> <issue_key(s)> [format]")
        print("Format options:")
        print("  - xml:  XML format (default)")
        print("  - json: JSON format")
        print("  - markdown: Markdown format")
        print("  - raw:  Raw Jira API response")
        print("\nExamples:")
        print("  Single issue: python jira_exporter.py YOUR-EMAIL:YOUR-TOKEN norbloc.atlassian.net PROJ-123 json")
        print("  Multiple issues: python jira_exporter.py YOUR-EMAIL:YOUR-TOKEN norbloc.atlassian.net \"PROJ-123,PROJ-124,PROJ-125\" json")
        sys.exit(1)

    token = sys.argv[1]
    server = sys.argv[2]
    issue_keys_input = sys.argv[3]
    format = sys.argv[4] if len(sys.argv) > 4 else 'xml'

    if format not in ['xml', 'json', 'markdown', 'raw']:
        print("Error: Format must be one of: xml, json, markdown, raw")
        sys.exit(1)

    # Parse issue keys - support both single issue and comma-separated list
    if ',' in issue_keys_input:
        issue_keys = [key.strip() for key in issue_keys_input.split(',')]
        logger.info(f"Processing multiple issues: {issue_keys}")
    else:
        issue_keys = [issue_keys_input.strip()]
        logger.info(f"Processing single issue: {issue_keys[0]}")

    try:
        exporter = JiraExporter(token, server)
        
        if len(issue_keys) == 1:
            # Single issue - maintain backward compatibility
            content = exporter.get_issue(issue_keys[0], format)
            
            if not content:
                logger.error(f"Failed to process issue {issue_keys[0]}")
                sys.exit(1)
            
            try:
                # Save file with appropriate extension
                ext = '.xml' if format == 'xml' else '.json' if format == 'json' else '.md' if format == 'markdown' else '.txt'
                output_file = f"{issue_keys[0]}_export{ext}"
                with open(output_file, "w") as f:
                    f.write(content)
                logger.info(f"{format.upper()} export saved to {output_file}")
            except IOError as e:
                logger.error(f"Failed to write output file: {str(e)}")
                sys.exit(1)
        else:
            # Multiple issues
            results = exporter.get_multiple_issues(issue_keys, format)
            
            success_count = 0
            for issue_key, content in results.items():
                if content:
                    try:
                        # Save file with appropriate extension
                        ext = '.xml' if format == 'xml' else '.json' if format == 'json' else '.md' if format == 'markdown' else '.txt'
                        output_file = f"{issue_key}_export{ext}"
                        with open(output_file, "w") as f:
                            f.write(content)
                        logger.info(f"{format.upper()} export for {issue_key} saved to {output_file}")
                        success_count += 1
                    except IOError as e:
                        logger.error(f"Failed to write output file for {issue_key}: {str(e)}")
                else:
                    logger.error(f"Failed to process issue {issue_key}")
            
            logger.info(f"Successfully exported {success_count} out of {len(issue_keys)} issues")
            
            if success_count == 0:
                sys.exit(1)
                
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
