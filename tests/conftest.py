import pytest

from main import mcp


@pytest.fixture
def mcp_server():
    """The production FastMCP server, so tests run the code that ships."""
    return mcp
