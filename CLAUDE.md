# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Model Context Protocol (MCP) server that intelligently splits Markdown documents into hierarchical sections while preserving parent-child relationships. The server is built using FastMCP and FastAPI, providing a single tool `split_text` that processes Markdown text.

## Instructions For Developers

Act as an experienced Software Engineer and Python Developer. 
Use industry best practices for code quality, security, and performance. Including but not limited to:
- Follow SOLID principles and design patterns.
- Use meaningful variable and function names.
- Write modular, reusable components.
- Implement error handling and logging.
- Ensure security best practices (e.g., input validation, sanitization).
- Optimize performance (e.g., lazy loading, caching).
- Write unit tests for critical functionality.
- Do not over-engineer the solution.

## Development Commands

### Setup
```bash
python -m venv .venv && source .venv/bin/activate
poetry install
```

### Testing
```bash
# Run all tests
poetry run pytest
# Or use the Makefile
make test
```

### Linting
```bash
# Run ruff for linting and formatting
poetry run ruff check .
# Or use the Makefile
make lint
```

### Running the Server
```bash
python src/main.py
```
The server starts on `http://0.0.0.0:8080` with the MCP server mounted at `/server/mcp`.

## Code Architecture

### Core Components

**`src/main.py`** - FastAPI application entry point
- Creates FastMCP server instance with `split_text` tool
- Mounts MCP server at `/server` path  
- Uses cached MarkdownSplitter instance via `@lru_cache`

**`src/settings.py`** - Logging configuration

The splitter comes from the `markdown-chunkify` library, and `split_text` returns its `Section` model unchanged (fields: `header`, `content`, `level`, and `metadata` with `id`, `parent_id`, `parents`, `span`, `char_count`; siblings are sections sharing a `parent_id`). Its source is at `~/Projects/markdown-chunkify`. Chunking bugs get fixed there, not here.

## MCP Integration

The server exposes one tool via MCP:
- **Tool**: `split_text`
- **Input**: `text: str` (Markdown content)
- **Output**: `List[Section]` with hierarchy metadata

Example MCP call:
```bash
curl -X POST http://localhost:8080/server/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "split_text", "arguments": {"text": "# Header\nContent"}}}'
```

## Testing Strategy

Tests are located in `tests/` and use pytest with async support:
- `test_splitter.py`: Tests of the `split_text` tool response (nesting, code blocks, empty input, siblings via `parent_id`, level-0 preamble, spans)
- Uses `fastmcp.Client` for MCP protocol testing
- All tests use the `mcp_server` fixture from `conftest.py`

## Dependencies

**Runtime**:
- `markdown-chunkify`: Markdown splitting (provides `MarkdownSplitter` and `Section`)
- `fastmcp`: MCP protocol implementation
- `fastapi`: Web framework
- `pydantic`: Data validation
- `uvicorn`: ASGI server

**Development**:
- `pytest` + `pytest-asyncio`: Testing framework
- `ruff`: Linting and formatting
- `black` + `isort`: Code formatting (configured via ruff)

## Configuration

**Ruff** (in `pyproject.toml`):
- Force single-line imports
- Double quote style
- Pytest path includes `src/`

**Python version**: >=3.12,<3.13