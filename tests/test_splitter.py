import json

import pytest
from fastmcp import Client

BASIC_MARKDOWN = """# Introduction
Welcome to the guide.

## Getting Started
First steps here.

## Advanced Topics
Advanced content here."""

NESTED_MARKDOWN = """# Main
Content

## Section A
A content

### Subsection A1
A1 content

## Section B
B content"""

CODE_BLOCK_MARKDOWN = """# Real Header
Some content

```python
# This is a comment, not a header
print("hello")
```

More content.
"""

SIBLINGS_MARKDOWN = """# Main
Content

## First
First content

## Second
Second content

## Third
Third content"""

TILDE_CODE_BLOCK_MARKDOWN = CODE_BLOCK_MARKDOWN.replace("```python", "~~~python").replace(
    "```", "~~~"
)


async def _split(client, text: str) -> list[dict]:
    result = await client.call_tool("split_text", {"text": text})
    if not result:
        return []
    data = json.loads(result[0].text)
    return data if isinstance(data, list) else [data]


@pytest.mark.asyncio
async def test_split_text_basic_functionality(mcp_server):
    """Test basic markdown splitting functionality."""
    async with Client(mcp_server) as client:
        sections = await _split(client, BASIC_MARKDOWN)

    assert len(sections) == 3

    assert sections[0]["header"] == "Introduction"
    assert sections[0]["content"] == "Welcome to the guide."
    assert sections[0]["level"] == 1
    assert sections[0]["metadata"]["parents"] == {}
    assert sections[0]["metadata"]["id"] == 0
    assert sections[0]["metadata"]["parent_id"] is None

    assert sections[1]["header"] == "Getting Started"
    assert sections[1]["level"] == 2
    assert sections[1]["metadata"]["parents"] == {"h1": "Introduction"}
    assert sections[1]["metadata"]["parent_id"] == 0


@pytest.mark.asyncio
async def test_split_text_nested_headers(mcp_server):
    """Test nested header hierarchy."""
    async with Client(mcp_server) as client:
        sections = await _split(client, NESTED_MARKDOWN)

    subsection = next(s for s in sections if s["header"] == "Subsection A1")
    assert subsection["level"] == 3
    assert subsection["metadata"]["parents"] == {"h1": "Main", "h2": "Section A"}
    assert subsection["metadata"]["parent_id"] == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("text", ["", "   \n"])
async def test_split_text_empty_input(mcp_server, text):
    """Test handling of empty input."""
    async with Client(mcp_server) as client:
        assert await _split(client, text) == []


@pytest.mark.asyncio
@pytest.mark.parametrize("text", [CODE_BLOCK_MARKDOWN, TILDE_CODE_BLOCK_MARKDOWN])
async def test_split_text_code_blocks_ignored(mcp_server, text):
    """Test that # in fenced code blocks are not treated as headers."""
    async with Client(mcp_server) as client:
        sections = await _split(client, text)

    assert len(sections) == 1
    assert sections[0]["header"] == "Real Header"
    assert "# This is a comment, not a header" in sections[0]["content"]
    assert "Some content" in sections[0]["content"]
    assert "More content" in sections[0]["content"]


@pytest.mark.asyncio
async def test_split_text_siblings_share_parent_id(mcp_server):
    """Test sibling sections share the same parent_id."""
    async with Client(mcp_server) as client:
        sections = await _split(client, SIBLINGS_MARKDOWN)

    children = [s for s in sections if s["level"] == 2]
    assert [s["header"] for s in children] == ["First", "Second", "Third"]
    assert all(s["metadata"]["parent_id"] == 0 for s in children)


@pytest.mark.asyncio
async def test_split_text_preamble_is_level_zero(mcp_server):
    async with Client(mcp_server) as client:
        sections = await _split(client, "Intro text\n# Title\nBody")
    assert sections[0]["header"] == ""
    assert sections[0]["level"] == 0
    assert sections[0]["content"] == "Intro text"
    assert sections[1]["header"] == "Title"
    assert sections[1]["metadata"]["parent_id"] is None


@pytest.mark.asyncio
async def test_split_text_duplicate_headers_kept_separate(mcp_server):
    text = "# A\n## Setup\na\n# B\n## Setup\nb"
    async with Client(mcp_server) as client:
        sections = await _split(client, text)
    setups = [s for s in sections if s["header"] == "Setup"]
    assert [s["content"] for s in setups] == ["a", "b"]
    assert [s["metadata"]["parent_id"] for s in setups] == [0, 2]


@pytest.mark.asyncio
async def test_split_text_span_indexes_input(mcp_server):
    async with Client(mcp_server) as client:
        sections = await _split(client, BASIC_MARKDOWN)
    start, end = sections[1]["metadata"]["span"]
    assert BASIC_MARKDOWN[start:end] == "## Getting Started\nFirst steps here."
    assert sections[1]["metadata"]["char_count"] == end - start
