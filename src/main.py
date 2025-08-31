from functools import lru_cache

import uvicorn
from fastapi import FastAPI
from fastmcp import FastMCP

from models import Section
from splitter import MarkdownSplitter


@lru_cache
def _splitter() -> MarkdownSplitter:
    """Returns a cached instance of MarkdownSplitter.
    
    Uses LRU cache to ensure only one instance is created for the application
    lifecycle, improving memory efficiency and performance.

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
    
    This MCP tool processes Markdown documents and returns a list of sections
    with preserved hierarchy, sibling relationships, and metadata. Each section
    includes the header text, content, level, and relationship information.
    
    Args:
        text: The Markdown text to process. Should contain headers marked with
              '#' symbols (e.g., "# Header 1", "## Header 2").
              
    Returns:
        A list of Section objects containing:
        - section_header: The header text without '#' markers
        - section_text: The content between this header and the next
        - header_level: The level of the header (1 for H1, 2 for H2, etc.)
        - metadata: Contains parent headers and sibling relationships
        
    Example:
        Input: "# Main\\nContent here\\n## Sub\\nSub content"
        Returns: [
            Section(section_header="Main", header_level=1, ...),
            Section(section_header="Sub", header_level=2, ...)
        ]
    """
    return markdown_splitter.split_text(text=text)


# Create the ASGI application for the MCP server
# The path="/mcp" sets the base path for MCP protocol endpoints
asgi_app = mcp.http_app(path="/mcp")

# Create a FastAPI application and mount the MCP server
# The lifespan parameter ensures proper startup/shutdown of the MCP server
app = FastAPI(
    title="Markdown MCP Server",
    description="A Model Context Protocol server for splitting Markdown documents",
    version="0.1.0",
    lifespan=asgi_app.lifespan
)

# Mount the MCP server at /server path
# Full MCP endpoints will be available at /server/mcp/*
app.mount("/server", asgi_app)


if __name__ == "__main__":
    # Start the server with uvicorn
    # Binds to all interfaces (0.0.0.0) on port 8080 for development
    uvicorn.run(app, host="0.0.0.0", port=8080)
