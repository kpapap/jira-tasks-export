# Contributing to Jira Task Exporter

Thank you for your interest in contributing to Jira Task Exporter! This document provides guidelines and information for contributors.

## Getting Started

### Prerequisites

- Python 3.6 or higher
- Git
- A Jira instance for testing (can be a test instance)

### Development Setup

1. Fork the repository
2. Clone your fork:

   ```bash
   git clone https://github.com/yourusername/jira-task-exporter.git
   cd jira-task-exporter
   ```

3. Create a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Install the package in development mode:
   ```bash
   pip install -e .
   ```

## Development Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and small
- Use type hints where appropriate

### Testing

- Write tests for new functionality
- Ensure all tests pass before submitting a pull request
- Test with different Jira instances and issue types
- Include edge cases in your tests

### Commit Messages

- Use clear and descriptive commit messages
- Start with a verb in present tense (e.g., "Add", "Fix", "Update")
- Keep the first line under 50 characters
- Include more details in the body if necessary

Example:

```
Add support for custom fields export

- Include custom fields in all export formats
- Add configuration option for field selection
- Update documentation with examples
```

## Submitting Changes

1. Create a new branch for your feature:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them:

   ```bash
   git add .
   git commit -m "Your commit message"
   ```

3. Push to your fork:

   ```bash
   git push origin feature/your-feature-name
   ```

4. Create a Pull Request on GitHub

### Pull Request Guidelines

- Provide a clear description of the changes
- Reference any related issues
- Include screenshots or examples if applicable
- Ensure all tests pass
- Update documentation if necessary

## Reporting Issues

When reporting issues, please include:

- Python version
- Jira version/type (Cloud, Server, Data Center)
- Steps to reproduce the issue
- Expected vs actual behavior
- Error messages or logs
- Sample code or configuration (without sensitive data)

## Feature Requests

For feature requests, please:

- Check if the feature already exists or is planned
- Describe the use case clearly
- Provide examples of how it would be used
- Consider if it fits the project's scope

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow the project's coding standards

## Questions?

If you have questions about contributing, feel free to:

- Open an issue for discussion
- Contact the maintainers
- Check existing documentation and issues

Thank you for contributing to Jira Task Exporter!
