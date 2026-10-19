from functools import lru_cache

import uvicorn
from fastapi import FastAPI
from fastmcp import FastMCP

from markdown_chunkify import MarkdownSplitter
from markdown_chunkify import Section
from settings import get_logger

logger = get_logger("MarkdownMCPServer")


@lru_cache
def _splitter() -> MarkdownSplitter:
    """Returns a cached instance of MarkdownSplitter.

    The library splitter is immutable, so one cached instance is safe to share
    across concurrent requests.

    Returns:
        MarkdownSplitter: A cached instance of the MarkdownSplitter class.
    """
    return MarkdownSplitter()


# Initialize FastMCP server with stateless HTTP support
# This enables the server to handle HTTP requests without maintaining session state
mcp = FastMCP("MarkdownMCPServer", stateless_http=True)
markdown_splitter = _splitter()


@mcp.tool
def split_text(text: str) -> list[Section]:
    """Split Markdown text into hierarchical sections.

    This MCP tool processes Markdown documents and returns a flat list of
    sections in document order. Each section carries its header, content, level,
    and hierarchy metadata (parent links and position in the input).

    Args:
        text: The Markdown text to process. Should contain headers marked with
              '#' symbols (e.g., "# Header 1", "## Header 2").

    Returns:
        A list of Section objects containing:
        - header: The header text without '#' markers (empty for pre-header text)
        - content: The content between this header and the next
        - level: The header level (1 for H1, 2 for H2, etc.; 0 for text before
          the first header)
        - metadata.id: The section's index in the returned list
        - metadata.parent_id: The id of the parent section, or null for top level
        - metadata.parents: Ancestor headers keyed by level (e.g. {"h1": "Main"})
        - metadata.span: [start, end] character offsets of the section in the input

    Example:
        Input: "# Main\\nContent here\\n## Sub\\nSub content"
        Returns: [
            Section(header="Main", level=1, metadata.id=0, metadata.parent_id=None, ...),
            Section(header="Sub", level=2, metadata.id=1, metadata.parent_id=0, ...)
        ]
    """
    logger.info(f"Processing split_text request with {len(text)} characters")
    try:
        sections = markdown_splitter.split_text(text=text)
        logger.info(f"Successfully processed request, returning {len(sections)} sections")
        return sections

    except Exception as e:
        logger.error(f"Error processing split_text request: {e}", exc_info=True)
        raise


# Create the ASGI application for the MCP server
# The path="/mcp" sets the base path for MCP protocol endpoints
asgi_app = mcp.http_app(path="/mcp")

# Create a FastAPI application and mount the MCP server
# The lifespan parameter ensures proper startup/shutdown of the MCP server
app = FastAPI(
    title="Markdown MCP Server",
    description="A Model Context Protocol server for splitting Markdown documents",
    version="0.2.0",
    lifespan=asgi_app.lifespan,
)

# Mount the MCP server at /server path
# Full MCP endpoints will be available at /server/mcp/*
app.mount("/server", asgi_app)


if __name__ == "__main__":
    # Start the server with uvicorn
    # Binds to all interfaces (0.0.0.0) on port 8080 for development
    logger.info("Starting Markdown MCP Server on http://0.0.0.0:8080")
    logger.info("MCP endpoints available at /server/mcp/")
    uvicorn.run(app, host="0.0.0.0", port=8080)
