[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)]
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/Gal-Gilor/markdown-mcp)

# Markdown MCP

A Model Context Protocol (MCP) server that intelligently splits Markdown documents into hierarchical sections while preserving parent-child relationships and sibling connections.

## Features

*   **Hierarchical splitting:** Maintains header relationships (H1 → H2 → H3...).
*   **Sibling detection:** Identifies headers at the same level.
*   **Code-aware:** Ignores `#` comments in code blocks.
*   **MCP compliant:** Standard Model Context Protocol interface.
*   **FastAPI powered:** High-performance async server.

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

To run the MCP server:

```bash
python src/main.py
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

## Development

This project includes a `Makefile` to simplify common development tasks.

- `make lint`: Run `ruff` to check for linting issues.
- `make test`: Run tests using `pytest`.

### Running Tests

This project uses `pytest` for testing. To run the tests:

```bash
poetry run pytest
```

Alternatively, you can use the Makefile:
```bash
make test
```