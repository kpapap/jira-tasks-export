#!/usr/bin/env python3

import json
import logging
from typing import Optional
import xmltodict

logger = logging.getLogger(__name__)

class JiraExporters:
    """Class containing all export format methods for Jira issues."""
    
    def __init__(self, jira_client):
        """Initialize with a Jira client instance."""
        self.jira = jira_client

    def to_json(self, issue, subtasks_data) -> Optional[str]:
        """Convert issue data to JSON format."""
        if not issue:
            return None
        
        try:
            # Create a dictionary with the same structure as XML for consistency
            # Fetch comments for the issue
            comments = []
            for comment in self.jira.comments(issue):
                comments.append({
                    'author': comment.author.displayName if comment.author else 'Unknown',
                    'body': comment.body,
                    'created': comment.created,
                    'updated': comment.updated
                })

            # Fetch remote links (web links)
            links = []
            for link in self.jira.remote_links(issue):
                links.append({
                    'title': link.object.title if hasattr(link.object, 'title') else '',
                    'url': link.object.url,
                    'relationship': link.relationship if hasattr(link, 'relationship') else 'Web Link'
                })

            issue_dict = {
                'issue': {
                    'key': issue.key,
                    'summary': issue.fields.summary,
                    'description': issue.fields.description or '',
                    'status': issue.fields.status.name,
                    'created': issue.fields.created,
                    'updated': issue.fields.updated,
                    'priority': issue.fields.priority.name if issue.fields.priority else 'None',
                    'assignee': issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned',
                    'reporter': issue.fields.reporter.displayName if issue.fields.reporter else 'Unknown',
                    'labels': issue.fields.labels if issue.fields.labels else [],
                    'type': issue.fields.issuetype.name,
                    'components': [c.name for c in issue.fields.components] if issue.fields.components else [],
                    'comments': comments,
                    'webLinks': links,
                    'subtasks': subtasks_data
                }
            }
            return json.dumps(issue_dict, indent=2)
        except Exception as e:
            logger.error(f"Failed to convert issue to JSON: {str(e)}")
            return None

    def to_xml(self, issue, subtasks_data) -> Optional[str]:
        """Convert issue data to XML format with enhanced field coverage."""
        if not issue:
            return None
        
        # Fetch comments for the issue
        comments = []
        for comment in self.jira.comments(issue):
            comments.append({
                'author': comment.author.displayName if comment.author else 'Unknown',
                'body': comment.body,
                'created': comment.created,
                'updated': comment.updated
            })
            
        # Fetch remote links (web links)
        links = []
        for link in self.jira.remote_links(issue):
            links.append({
                'title': link.object.title if hasattr(link.object, 'title') else '',
                'url': link.object.url,
                'relationship': link.relationship if hasattr(link, 'relationship') else 'Web Link'
            })
            
        # Enhanced issue dictionary with more fields
        issue_dict = {
            'issue': {
                'key': issue.key,
                'summary': issue.fields.summary,
                'description': issue.fields.description or '',
                'status': issue.fields.status.name,
                'created': issue.fields.created,
                'updated': issue.fields.updated,
                'priority': issue.fields.priority.name if issue.fields.priority else 'None',
                'assignee': issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned',
                'reporter': issue.fields.reporter.displayName if issue.fields.reporter else 'Unknown',
                'labels': {'label': issue.fields.labels} if issue.fields.labels else {'label': []},
                'type': issue.fields.issuetype.name,
                'components': {
                    'component': [c.name for c in issue.fields.components]
                } if issue.fields.components else {'component': []},
                'comments': {
                    'comment': comments
                } if comments else {'comment': []},
                'webLinks': {
                    'link': links
                } if links else {'link': []},
                'subtasks': {
                    'subtask': subtasks_data
                } if subtasks_data else {'subtask': []}
            }
        }
        
        try:
            return xmltodict.unparse(issue_dict, pretty=True)
        except Exception as e:
            logger.error(f"Failed to convert issue to XML: {str(e)}")
            return None

    def json_to_markdown(self, json_content: str) -> Optional[str]:
        """Convert JSON export to Markdown format."""
        try:
            data = json.loads(json_content)
            issue = data['issue']
            
            # Build markdown content
            md_content = f"""# {issue['key']} - {issue['summary']}

## Issue Details
- **Type:** {issue['type']}
- **Status:** {issue['status']}
- **Priority:** {issue['priority']}

## People
- **Assignee:** {issue['assignee']}
- **Reporter:** {issue['reporter']}

## Dates
- **Created:** {issue['created']}
- **Updated:** {issue['updated']}

## Labels
{'None' if not issue['labels'] else '\\n'.join(f'- {label}' for label in issue['labels'])}

## Components
{'None' if not issue['components'] else '\\n'.join(f'- {comp}' for comp in issue['components'])}

## Description
{issue['description']}

## Comments
"""
            if issue.get('comments'):
                for comment in issue['comments']:
                    md_content += f"""### {comment['author']} - {comment['created']}
{comment['body']}

"""

            if issue.get('webLinks'):
                md_content += "\n## Related Links\n"
                for link in issue['webLinks']:
                    md_content += f"- [{link['title']}]({link['url']}) ({link['relationship']})\n"

            if issue.get('subtasks'):
                md_content += "\n## Related Issues\n"
                # Group issues by relationship type
                relationship_groups = {}
                for related in issue['subtasks']:
                    rel_type = related['relationship']
                    if rel_type not in relationship_groups:
                        relationship_groups[rel_type] = []
                    relationship_groups[rel_type].append(related)
                
                # Output each group
                for rel_type, issues in relationship_groups.items():
                    md_content += f"\n### {rel_type.capitalize()}\n"
                    for issue_item in issues:
                        md_content += f"\n#### [{issue_item['key']}] {issue_item['summary']}\n"
                        md_content += f"- **Status:** {issue_item['status']}\n"
                        md_content += f"- **Type:** {issue_item['type']}\n"
                        if issue_item.get('assignee'):
                            md_content += f"- **Assignee:** {issue_item['assignee']}\n"
                        if issue_item.get('priority'):
                            md_content += f"- **Priority:** {issue_item['priority']}\n"
                        if issue_item.get('components'):
                            md_content += f"- **Components:** {', '.join(issue_item['components'])}\n"
                        if issue_item.get('labels'):
                            md_content += f"- **Labels:** {', '.join(issue_item['labels'])}\n"
                        md_content += f"- **Created:** {issue_item['created']}\n"
                        md_content += f"- **Updated:** {issue_item['updated']}\n"
                        if issue_item.get('description'):
                            md_content += f"\n{issue_item['description']}\n\n"

            return md_content
        except Exception as e:
            logger.error(f"Failed to convert JSON to Markdown: {str(e)}")
            return None
