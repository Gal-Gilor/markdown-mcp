#!/usr/bin/env python3
"""An example Python client for the Markdown MCP server.

This script demonstrates how to connect to and use the Markdown MCP server
from a Python application. It shows both basic usage and advanced patterns.
"""

import asyncio
import json
from typing import Dict
from typing import List

import httpx


class MarkdownMCPClient:
    """Client for interacting with the Markdown MCP server."""

    def __init__(self, base_url: str = "http://localhost:8080"):
        """Initialize the client with the server URL."""
        self.base_url = base_url
        self.mcp_url = f"{base_url}/server/mcp/"

    async def split_text(self, text: str) -> List[Dict]:
        """Split markdown text using the MCP server."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "split_text", "arguments": {"text": text}},
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.mcp_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                },
            )
            response.raise_for_status()

            # Parse SSE response
            response_text = response.text.strip()
            if response_text.startswith("event: message") and "data: " in response_text:
                # Extract data part from SSE format
                data_start = response_text.find("data: ") + len("data: ")
                data_part = response_text[data_start:]
                result = json.loads(data_part)
                # Extract the actual result from MCP response
                sections_data = result["result"]["content"][0]["text"]
                # Parse the JSON string containing the sections
                sections = json.loads(sections_data)
                # Convert single section dict to list, or return list as-is
                return sections if isinstance(sections, list) else [sections]
            elif response_text:
                # Try parsing as regular JSON
                result = json.loads(response_text)
                return result["result"] if "result" in result else result
            else:
                raise ValueError("Empty response from server")


async def example_basic_usage():
    """Demonstrate basic usage of the MCP client."""
    print("=== Basic Usage Example ===")

    markdown_text = """
# Introduction
Welcome to the Markdown MCP server example.

## Getting Started
This section covers the basics.

### Installation
Run the following commands:
```bash
# Install dependencies
pip install -r requirements.txt
```

### Configuration
Set up your configuration file.

## Advanced Usage
This section covers advanced topics.

### API Integration
Learn how to integrate with the API.

### Custom Processors
Build your own processors.
"""

    client = MarkdownMCPClient()

    try:
        sections = await client.split_text(markdown_text)

        print(f"Split document into {len(sections)} sections:\n")

        for i, section in enumerate(sections, 1):
            print(f"Section {i}:")
            print(f"  Header: {section['section_header']}")
            print(f"  Level: {section['header_level']}")
            print(f"  Parents: {section['metadata']['parents']}")
            print(f"  Siblings: {section['metadata']['siblings']}")
            print(f"  Content: {section['section_text'][:50]}...")
            print()

    except Exception as e:
        print(f"Error: {e}")


async def example_document_analysis():
    """Demonstrate document analysis patterns."""
    print("=== Document Analysis Example ===")

    # Sample technical documentation
    markdown_text = """
# API Documentation

This is the main API documentation.

## Authentication
All API requests require authentication.

### API Keys
Use API keys for authentication.

### OAuth2
OAuth2 is also supported.

## Endpoints

### Users
User management endpoints.

#### GET /users
Retrieve all users.

#### POST /users
Create a new user.

### Projects
Project management endpoints.

#### GET /projects
List all projects.

## Rate Limits
API rate limits apply.
"""

    client = MarkdownMCPClient()

    try:
        sections = await client.split_text(markdown_text)

        # Analyze document structure
        print("Document Structure Analysis:")
        print("-" * 40)

        # Group by level
        levels = {}
        for section in sections:
            level = section["header_level"]
            if level not in levels:
                levels[level] = []
            levels[level].append(section["section_header"])

        for level in sorted(levels.keys()):
            indent = "  " * (level - 1)
            print(f"Level {level} headers:")
            for header in levels[level]:
                print(f"{indent}- {header}")

        print("\nSibling Relationships:")
        print("-" * 40)
        for section in sections:
            if section["metadata"]["siblings"]:
                print(
                    f"'{section['section_header']}' has siblings: {section['metadata']['siblings']}"
                )

        print("\nParent-Child Relationships:")
        print("-" * 40)
        for section in sections:
            if section["metadata"]["parents"]:
                parents_str = " → ".join(
                    [f"{k.upper()}: {v}" for k, v in section["metadata"]["parents"].items()]
                )
                print(f"'{section['section_header']}' parents: {parents_str}")

    except Exception as e:
        print(f"Error: {e}")


async def main():
    """Run all examples."""
    print("Markdown MCP Server - Python Client Examples")
    print("=" * 50)
    print()

    await example_basic_usage()
    print()
    await example_document_analysis()


if __name__ == "__main__":
    asyncio.run(main())
