from functools import lru_cache

import uvicorn
from fastapi import FastAPI
from fastmcp import FastMCP

from models import Section
from splitter import MarkdownSplitter


@lru_cache
def _splitter() -> MarkdownSplitter:
    """Returns an instance of MarkdownSplitter.

    Returns:
        MarkdownSplitter: A new instance of the MarkdownSplitter class.
    """

    return MarkdownSplitter()


mcp = FastMCP("MyServer", stateless_http=True)
markdown_splitter = _splitter()


@mcp.tool
def split_text(text: str) -> list[Section]:
    """Splits Markdown text"""

    return markdown_splitter.split_text(text=text)


# Create the ASGI app
asgi_app = mcp.http_app(path="/mcp")


# Create a FastAPI app and mount the MCP server
app = FastAPI(lifespan=asgi_app.lifespan)
app.mount("/server", asgi_app)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
