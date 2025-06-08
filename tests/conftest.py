import pytest
from fastmcp import FastMCP

from models import Section
from splitter import MarkdownSplitter


@pytest.fixture
def mcp_server():
    """Create a test FastMCP server with the split_text tool."""
    server = FastMCP("TestServer")

    @server.tool
    def split_text(text: str) -> list[Section]:
        """Splits Markdown text"""
        return MarkdownSplitter().split_text(text)

    return server
