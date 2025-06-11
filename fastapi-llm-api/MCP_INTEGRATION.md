# MCP Tools Integration for FastAPI LLM API

This document describes the Model Context Protocol (MCP) tools integration added to the FastAPI LLM API.

## Overview

The MCP integration allows the LLM to use various external tools and services to provide more comprehensive and accurate responses. The integration supports:

- **Notion API**: Search pages and databases, query database contents
- **Web Search**: Real-time web search capabilities
- **File Operations**: Read files and search codebase
- **Database Operations**: Query Notion databases with filters

## Architecture

### Components

1. **MCP Integration Module** (`mcp_integration.py`)
   - `MCPToolRegistry`: Central registry for managing tools
   - Tool handlers for each MCP function
   - Standardized result format with `MCPToolResult`

2. **Enhanced LLM App** (`llm_app.py`)
   - Modified to support tool-enabled conversations
   - Dual endpoints for with/without tools
   - Health check and tool discovery endpoints

3. **Test Suite** (`test_mcp_integration.py`)
   - Comprehensive tests for all tool handlers
   - Registry functionality validation

## Available Tools

### 1. Notion Search (`notion_search`)
Search for pages or databases in Notion by title.

**Parameters:**
- `query` (required): Search term
- `filter_type` (optional): "page" or "database"

**Example:**
```python
{
    "query": "project documentation",
    "filter_type": "page"
}
```

### 2. Web Search (`web_search`)
Search the web for real-time information.

**Parameters:**
- `search_term` (required): What to search for

**Example:**
```python
{
    "search_term": "latest AI developments 2024"
}
```

### 3. File Read (`file_read`)
Read contents of a file with optional line range.

**Parameters:**
- `file_path` (required): Path to the file
- `start_line` (optional): Starting line number
- `end_line` (optional): Ending line number

**Example:**
```python
{
    "file_path": "src/main.py",
    "start_line": 1,
    "end_line": 50
}
```

### 4. Codebase Search (`codebase_search`)
Search for code patterns in the codebase.

**Parameters:**
- `query` (required): Search pattern
- `directories` (optional): Specific directories to search

**Example:**
```python
{
    "query": "class definition",
    "directories": ["src", "lib"]
}
```

### 5. Database Query (`database_query`)
Query a Notion database with optional filters.

**Parameters:**
- `database_id` (required): Notion database ID
- `filter_conditions` (optional): Query filters

**Example:**
```python
{
    "database_id": "abc123",
    "filter_conditions": {
        "property": "Status",
        "select": {"equals": "Done"}
    }
}
```

## API Endpoints

### Primary Endpoints

#### `POST /api/question`
Main endpoint with MCP tools enabled.

**Request:**
```json
{
    "question": "What are the latest developments in AI?"
}
```

**Response:**
```json
{
    "question": "What are the latest developments in AI?",
    "answer": "Based on recent web search results...",
    "thought": "I should search for recent AI developments",
    "topic": "artificial intelligence"
}
```

#### `POST /api/question_no_tools`
Legacy endpoint without MCP tools.

### Utility Endpoints

#### `GET /api/mcp/tools`
Get list of available MCP tools.

**Response:**
```json
{
    "available_tools": 5,
    "tools": [
        {
            "name": "notion_search",
            "description": "Search for pages or databases in Notion by title",
            "parameters": ["query", "filter_type"]
        }
    ]
}
```

#### `GET /api/health`
Health check with MCP status.

**Response:**
```json
{
    "status": "healthy",
    "mcp_tools_available": 5,
    "service": "FastAPI LLM with MCP Tools"
}
```

## Usage Examples

### Starting the Server
```bash
cd fastapi-llm-api
python llm_app.py
```

### Testing MCP Integration
```bash
python test_mcp_integration.py
```

### Example API Call
```bash
curl -X POST "http://localhost:8888/api/question" \
     -H "Content-Type: application/json" \
     -d '{"question": "Search for project documentation in Notion"}'
```

## How It Works

1. **Question Processing**: When a question is received, the LLM first determines if tools are needed
2. **Tool Selection**: The LLM chooses appropriate tools based on the question context
3. **Tool Execution**: Selected tools are executed with proper parameters
4. **Result Integration**: Tool results are integrated into the final response
5. **Structured Output**: The response is formatted according to the `QAAnalytics` schema

## Configuration

### Environment Variables
Ensure you have the required environment variables for:
- OpenAI API key
- Notion API token (when using real Notion integration)

### Adding New Tools

1. Define the tool schema in `mcp_integration.py`:
```python
NEW_TOOL = {
    "type": "function",
    "function": {
        "name": "new_tool",
        "description": "Description of the new tool",
        "parameters": {
            # Parameter schema
        }
    }
}
```

2. Create a handler function:
```python
def handle_new_tool(param1, param2):
    # Tool implementation
    return result_dict
```

3. Register the tool:
```python
mcp_registry.register_tool(NEW_TOOL, handle_new_tool)
```

## Limitations and TODOs

### Current Limitations
- Tool handlers are currently mock implementations
- Limited error handling for malformed tool calls
- No authentication for external services

### TODOs
- [ ] Integrate with actual MCP function implementations
- [ ] Add authentication and rate limiting
- [ ] Implement caching for frequently used tools
- [ ] Add more comprehensive error handling
- [ ] Support for streaming responses with tools
- [ ] Tool usage analytics and monitoring

## Testing

Run the test suite to verify MCP integration:

```bash
python test_mcp_integration.py
```

The test suite covers:
- Tool registry initialization
- Individual tool handlers
- Tool execution flow
- Error handling
- Tool definition validation

## Contributing

When adding new MCP tools:

1. Follow the existing pattern in `mcp_integration.py`
2. Add comprehensive tests
3. Update this documentation
4. Ensure proper error handling
5. Test integration with the LLM

## Troubleshooting

### Common Issues

1. **Tools not loading**: Check that `initialize_mcp_tools()` is called
2. **Tool execution errors**: Verify tool parameters match the schema
3. **Import errors**: Ensure `mcp_integration.py` is in the same directory

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This will show detailed information about tool registration and execution. 