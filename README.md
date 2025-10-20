[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Execute Tests](https://github.com/Gal-Gilor/markdown-mcp/actions/workflows/execute_main_tests.yaml/badge.svg)](https://github.com/Gal-Gilor/markdown-mcp/actions/workflows/execute_main_tests.yaml)
[![Deploy to Cloud Run](https://github.com/Gal-Gilor/markdown-mcp/actions/workflows/deploy_main.yaml/badge.svg)](https://github.com/Gal-Gilor/markdown-mcp/actions/workflows/deploy_main.yaml)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/Gal-Gilor/markdown-mcp)

# Markdown MCP Server

> **Learn MCP Development by Example** 📚  
> A complete, production-ready Model Context Protocol (MCP) server that demonstrates best practices for building intelligent document processing tools.

## 🎯 What is this?

This is a **Model Context Protocol (MCP) server** that intelligently splits Markdown documents into hierarchical sections while preserving parent-child relationships and sibling connections. Built with FastMCP and FastAPI, it serves as both a useful tool and an educational resource for developers learning to create their own MCP servers. The project includes automated testing and deployment via GitHub Actions workflows.

### Why MCP?

The Model Context Protocol enables AI assistants to access external tools and data sources securely and efficiently. This server demonstrates how to:
- Build MCP-compliant tools that AI models can use
- Handle structured document processing
- Maintain relationships in hierarchical data
- Integrate with modern Python web frameworks

## Features

### Core Functionality
- **Hierarchical Splitting**: Maintains header relationships (H1 → H2 → H3...)
- **Sibling Detection**: Identifies headers at the same level for navigation
- **Code-Aware Processing**: Ignores `#` comments in fenced code blocks
- **Rich Metadata**: Includes parent references, sibling lists, and optional token counts

### Technical Stack
- **MCP Compliant**: Full Model Context Protocol interface support
- **FastAPI Powered**: High-performance async server with automatic OpenAPI docs
- **Well Tested**: Core splitting functionality covered with pytest
- **Type Safety**: Complete type hints with Pydantic models
- **Docker Ready**: Containerized deployment support
- **CI/CD**: Automated testing and deployment via GitHub Actions

## Requirements

*   Python >=3.12, <3.13

## Quick Start

This project uses [Poetry](https://python-poetry.org/) for dependency management. To get started:

```bash
git clone https://github.com/Gal-Gilor/markdown-mcp.git
cd markdown-mcp
python -m venv .venv && source .venv/bin/activate
poetry install
python src/main.py
```

## Usage

To run the MCP server (if the environment is activated):

```bash
python src/main.py
```

If the environment is not activated, you can run using Poetry:
```bash
poetry run python src/main.py
```


- The server will start on `http://0.0.0.0:8080`.
- The MCP server is mounted at `/server`. 
- The MCP server is accessible at `/server/mcp`.
- Available tools:

    *   **`split_text(text: str) -> list[Section]`**: Splits the input Markdown `text` into a list of `Section` objects.
        ```json
        {
            "section_header": "Getting Started",
            "section_text": "Welcome to the guide...",
            "header_level": 2,
            "metadata": {
                "parents": {"h1": "Introduction"},
                "siblings": ["Advanced Topics", "FAQ"]
            }
        }
        ```

        **Example Request:**
        ```bash
        curl -X POST http://localhost:8080/server/mcp/tools/call \
        -H "Content-Type: application/json" \
        -H "Accept: application/json, text/event-stream" \
        -d '{
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
            "name": "split_text",
            "arguments": {
                "text": "# Header 1\n\nSome content here.\n\n## Header 2\n\nMore content."
            }
            }
        }'
        ```

## Architecture Overview

### Project Structure
```
src/
├── main.py          # FastAPI app and MCP server setup
├── models.py        # Pydantic data models
└── splitter.py      # Core splitting logic

tests/
├── conftest.py      # Test fixtures
└── test_splitter.py # Splitter functionality tests
```

### Key Components

- **FastMCP Integration**: Uses `@mcp.tool` decorator to expose functions as MCP tools
- **Pydantic Models**: Type-safe data structures with validation
- **Hierarchical Processing**: Two-pass algorithm for building document structure
- **Code Block Protection**: Regex-based approach to ignore comments in code

### How It Works

1. **Code Block Processing**: Protects `#` comments in fenced code blocks
2. **Header Detection**: Uses regex pattern `^(#+)\s+(.+)$` to find headers
3. **Hierarchy Building**: Maintains parent-child relationships using a stack
4. **Sibling Detection**: Groups headers at same level with same parent
5. **Section Creation**: Converts hierarchical structure to flat list of sections

## Development

### Setup
```bash
python -m venv .venv && source .venv/bin/activate
poetry install
```

### Commands
- `make lint`: Run ruff for code formatting and linting
- `make test`: Run pytest test suite
- `python src/main.py`: Start the development server

### Testing
```bash
# Run all tests
poetry run pytest

# Run with verbose output
poetry run pytest -v

# Run specific test file
poetry run pytest tests/test_splitter.py
```

### CI/CD

The project includes GitHub Actions workflows for automated testing and deployment:

- **Execute Tests** (`.github/workflows/execute_main_tests.yaml`): Runs pytest test suite on push/PR to main branch
- **Deploy to Cloud Run** (`.github/workflows/deploy_main.yaml`): Automatically deploys to Google Cloud Run on push to main branch