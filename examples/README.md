# MCP Client Examples

This directory contains example client implementations for the Markdown MCP server in different programming languages.

## Available Examples

### Python Client (`python_example.py`)
A comprehensive Python client demonstrating:
- Basic text splitting functionality
- Document structure analysis  
- Hierarchical relationship exploration
- Error handling patterns

**Requirements:**
- Python 3.12+
- Project dependencies (installed via Poetry)

**Usage:**
```bash
# Start the MCP server first
poetry run python src/main.py

# Run the Python examples (from project root)
poetry run python examples/python_example.py
```

### JavaScript Client (`javascript_example.js`)
A Node.js client showing:
- Basic usage with built-in fetch API
- Table of contents generation
- Content analysis and statistics
- Document structure visualization

**Requirements:**
- Node.js 18+ (for built-in fetch support)
- No additional dependencies

**Usage:**
```bash
# Start the MCP server first
poetry run python src/main.py

# Run the JavaScript examples  
node examples/javascript_example.js
```

## Example Use Cases

### 1. Document Processing Pipeline
Use the MCP server as part of a larger document processing system:
```python
# Process multiple documents
documents = load_documents()
for doc in documents:
    sections = await client.split_text(doc.content)
    process_sections(sections)
```

### 2. Content Management System
Generate navigation structures for documentation:
```javascript
const sections = await client.splitText(markdownContent);
const navigation = generateNavigation(sections);
```

### 3. API Documentation Generator
Extract and organize API documentation sections:
```python
api_docs = await client.split_text(api_markdown)
endpoints = extract_endpoints(api_docs)
```

## Integration Patterns

### Error Handling
Both examples demonstrate proper error handling for:
- Network connectivity issues
- Server unavailability  
- Invalid response formats
- Malformed markdown input

### Async/Await Usage
Modern async patterns for:
- Non-blocking HTTP requests
- Concurrent document processing
- Streaming large documents

### Type Safety
Python example shows:
- Type hints for better IDE support
- Structured data handling
- Response validation

## Testing Your Integration

1. **Start the server:**
   ```bash
   poetry run python src/main.py
   ```

2. **Verify server is running:**
   ```bash
   curl http://localhost:8080/server/mcp/
   ```

3. **Run examples:**
   ```bash
   # Python
   poetry run python examples/python_example.py
   
   # JavaScript  
   node examples/javascript_example.js
   ```

## Extending the Examples

### Adding New Languages
To add support for other languages:
1. Implement HTTP client for MCP JSON-RPC protocol
2. Handle the `tools/call` endpoint  
3. Parse the response structure
4. Add error handling for network issues

### Custom Processing
Extend the examples with:
- Content filtering based on header levels
- Section merging and splitting
- Custom metadata extraction
- Integration with other tools

## Troubleshooting

### Common Issues

**Connection Refused:**
- Ensure MCP server is running: `poetry run python src/main.py`
- Check server is accessible at `http://localhost:8080`

**Import Errors (Python):**
- Install dependencies: `poetry install`  
- Check Python version: `python --version` (needs 3.12+)
- Activate environment: `poetry shell` or use `poetry run`

**Fetch Errors (JavaScript):**
- Use Node.js 18+ for built-in fetch support
- For older Node.js versions, install `node-fetch`

**Invalid JSON Response:**
- Verify server is running the correct version
- Check request format matches MCP specification
- Review server logs for errors