[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Execute Tests](https://github.com/Gal-Gilor/markdown-mcp/actions/workflows/execute_main_tests.yaml/badge.svg)](https://github.com/Gal-Gilor/markdown-mcp/actions/workflows/execute_main_tests.yaml)
[![Deploy to Cloud Run](https://github.com/Gal-Gilor/markdown-mcp/actions/workflows/deploy_main.yaml/badge.svg)](https://github.com/Gal-Gilor/markdown-mcp/actions/workflows/deploy_main.yaml)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/Gal-Gilor/markdown-mcp)

# Markdown MCP Server

> **Learn MCP Development by Example**
> A complete, production-ready Model Context Protocol (MCP) server that demonstrates best practices for building intelligent document processing tools.

## What is this?

This is a **Model Context Protocol (MCP) server** that intelligently splits Markdown documents into hierarchical sections while preserving parent-child relationships. Built with FastMCP and FastAPI, it serves as both a useful tool and an educational resource for developers learning to create their own MCP servers. The project includes automated testing and deployment via GitHub Actions workflows.

### Why MCP?

The Model Context Protocol enables AI assistants to access external tools and data sources securely and efficiently. This server demonstrates how to:
- Build MCP-compliant tools that AI models can use
- Handle structured document processing
- Maintain relationships in hierarchical data
- Integrate with modern Python web frameworks

## Features

### Core Functionality
- **Hierarchical Splitting**: Maintains header relationships (H1 → H2 → H3...)
- **Sibling Navigation**: Sections that share a `parent_id` are siblings
- **Code-Aware Processing**: Ignores `#` comments in fenced code blocks
- **Rich Metadata**: Includes parent references and character offsets into the input

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
            "header": "Getting Started",
            "content": "Install it.",
            "level": 2,
            "metadata": {
                "id": 1,
                "parent_id": 0,
                "parents": {"h1": "Introduction"},
                "span": [25, 55],
                "char_count": 30
            }
        }
        ```

        `level` is `0` for text before the first header. `metadata.id` is the section's position in document order, `parent_id` is the id of the enclosing section (`null` at the top level), and `span` is the `[start, end)` character range of the section in the input `text`. Siblings are the sections that share the same `parent_id`.

        **Example Request:**
        ```bash
        curl -X POST http://localhost:8080/server/mcp/ \
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
└── settings.py      # Logging configuration

tests/
├── conftest.py      # Test fixtures
└── test_splitter.py # split_text tool tests
```

Chunking is provided by the [`markdown-chunkify`](https://pypi.org/project/markdown-chunkify/) library; this server wraps it as an MCP tool and returns its `Section` model unchanged.

### Key Components

- **FastMCP Integration**: Uses `@mcp.tool` decorator to expose functions as MCP tools
- **markdown-chunkify**: Splits Markdown into hierarchical sections and ignores `#` comments in fenced code blocks
- **Cached Splitter**: One immutable `MarkdownSplitter` instance is shared across requests

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