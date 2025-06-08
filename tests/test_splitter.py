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

EMPTY_MARKDOWN = ""


@pytest.mark.asyncio
async def test_split_text_basic_functionality(mcp_server):
    """Test basic markdown splitting functionality."""
    async with Client(mcp_server) as client:
        result = await client.call_tool("split_text", {"text": BASIC_MARKDOWN})

        data = json.loads(result[0].text)
        # Normalize: ensure we always work with a list
        sections = data if isinstance(data, list) else [data]

        assert len(sections) == 3

        # Check first section
        assert sections[0]["section_header"] == "Introduction"
        assert sections[0]["section_text"] == "Welcome to the guide."
        assert sections[0]["header_level"] == 1
        assert sections[0]["metadata"]["parents"] == {}

        # Check second section
        assert sections[1]["section_header"] == "Getting Started"
        assert sections[1]["header_level"] == 2
        assert sections[1]["metadata"]["parents"] == {"h1": "Introduction"}
        assert "Advanced Topics" in sections[1]["metadata"]["siblings"]


@pytest.mark.asyncio
async def test_split_text_nested_headers(mcp_server):
    """Test nested header hierarchy."""
    async with Client(mcp_server) as client:
        result = await client.call_tool("split_text", {"text": NESTED_MARKDOWN})

        data = json.loads(result[0].text)
        sections = data if isinstance(data, list) else [data]

        # Find the subsection
        subsection = next(s for s in sections if s["section_header"] == "Subsection A1")

        assert subsection["header_level"] == 3
        assert subsection["metadata"]["parents"] == {"h1": "Main", "h2": "Section A"}


@pytest.mark.asyncio
async def test_split_text_empty_input(mcp_server):
    """Test handling of empty input."""
    async with Client(mcp_server) as client:
        result = await client.call_tool("split_text", {"text": EMPTY_MARKDOWN})

        if result:
            data = json.loads(result[0].text)
            sections = data if isinstance(data, list) else [data]
            assert sections == []
        else:
            assert len(result) == 0


@pytest.mark.asyncio
async def test_split_text_code_blocks_ignored(mcp_server):
    """Test that # in code blocks are not treated as headers."""
    async with Client(mcp_server) as client:
        result = await client.call_tool("split_text", {"text": CODE_BLOCK_MARKDOWN})

        data = json.loads(result[0].text)
        sections = data if isinstance(data, list) else [data]

        # Should be exactly one section
        assert len(sections) == 1

        # Verify it's the real header, not the comment
        assert sections[0]["section_header"] == "Real Header"
        assert sections[0]["header_level"] == 1
        assert "Some content" in sections[0]["section_text"]
        assert "More content" in sections[0]["section_text"]


@pytest.mark.asyncio
async def test_split_text_siblings_detection(mcp_server):
    """Test sibling relationships are correctly identified."""
    async with Client(mcp_server) as client:
        result = await client.call_tool("split_text", {"text": SIBLINGS_MARKDOWN})

        data = json.loads(result[0].text)
        sections = data if isinstance(data, list) else [data]

        # Find the "Second" section
        second_section = next(s for s in sections if s["section_header"] == "Second")
        siblings = second_section["metadata"]["siblings"]

        assert "First" in siblings
        assert "Third" in siblings
        assert len(siblings) == 2
