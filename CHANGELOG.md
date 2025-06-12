# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
[1.1.0]: https://github.com/kpapap/jira-tasks-export/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/kpapap/jira-tasks-export/releases/tag/v1.0.0
