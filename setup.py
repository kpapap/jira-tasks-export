#!/usr/bin/env python3
"""Setup script for Jira Task Exporter."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="jira-task-exporter",
    version="1.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool to export Jira tasks in multiple formats (XML, JSON, Markdown, Raw)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/jira-task-exporter",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Groupware",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "jira-exporter=jira_exporter:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
