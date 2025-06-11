"""
Test file for MCP integration
"""

import pytest
import json
from unittest.mock import Mock, patch
from mcp_integration import (
    mcp_registry, 
    execute_mcp_tool_call,
    handle_notion_search,
    handle_web_search,
    handle_file_read,
    handle_codebase_search,
    handle_database_query
)


def test_mcp_registry_initialization():
    """Test that MCP registry is properly initialized"""
    assert len(mcp_registry.tools) > 0
    assert len(mcp_registry.handlers) > 0
    assert len(mcp_registry.tools) == len(mcp_registry.handlers)


def test_notion_search_handler():
    """Test Notion search handler"""
    result = handle_notion_search("test query", "page")
    
    assert "query" in result
    assert "filter_type" in result
    assert result["query"] == "test query"
    assert result["filter_type"] == "page"


def test_web_search_handler():
    """Test web search handler"""
    result = handle_web_search("python programming")
    
    assert "search_term" in result
    assert "results" in result
    assert result["search_term"] == "python programming"
    assert isinstance(result["results"], list)


def test_file_read_handler():
    """Test file read handler"""
    result = handle_file_read("test.py", 1, 10)
    
    assert "file_path" in result
    assert "start_line" in result
    assert "end_line" in result
    assert result["file_path"] == "test.py"
    assert result["start_line"] == 1
    assert result["end_line"] == 10


def test_codebase_search_handler():
    """Test codebase search handler"""
    result = handle_codebase_search("function definition", ["src", "lib"])
    
    assert "query" in result
    assert "directories" in result
    assert "matches" in result
    assert result["query"] == "function definition"
    assert result["directories"] == ["src", "lib"]


def test_database_query_handler():
    """Test database query handler"""
    filter_conditions = {"property": "Status", "select": {"equals": "Done"}}
    result = handle_database_query("db123", filter_conditions)
    
    assert "database_id" in result
    assert "filter" in result
    assert "results" in result
    assert result["database_id"] == "db123"
    assert result["filter"] == filter_conditions


def test_execute_mcp_tool_call():
    """Test MCP tool call execution"""
    # Create a mock tool call
    mock_tool_call = Mock()
    mock_tool_call.function.name = "web_search"
    mock_tool_call.function.arguments = json.dumps({"search_term": "AI tools"})
    
    result_str = execute_mcp_tool_call(mock_tool_call)
    result = json.loads(result_str)
    
    assert result["status"] == "success"
    assert result["tool"] == "web_search"
    assert "data" in result


def test_tool_registry_execution():
    """Test tool execution through registry"""
    result = mcp_registry.execute_tool("notion_search", {"query": "test"})
    
    assert result.success is True
    assert result.tool_name == "notion_search"
    assert result.data is not None


def test_unknown_tool_execution():
    """Test execution of unknown tool"""
    result = mcp_registry.execute_tool("unknown_tool", {})
    
    assert result.success is False
    assert "Unknown tool" in result.error_message


def test_tool_definitions_format():
    """Test that tool definitions have correct format"""
    tools = mcp_registry.get_tool_definitions()
    
    for tool in tools:
        assert "type" in tool
        assert tool["type"] == "function"
        assert "function" in tool
        assert "name" in tool["function"]
        assert "description" in tool["function"]
        assert "parameters" in tool["function"]


if __name__ == "__main__":
    # Run basic tests
    print("Testing MCP integration...")
    
    test_mcp_registry_initialization()
    print("✓ Registry initialization test passed")
    
    test_notion_search_handler()
    print("✓ Notion search handler test passed")
    
    test_web_search_handler()
    print("✓ Web search handler test passed")
    
    test_file_read_handler()
    print("✓ File read handler test passed")
    
    test_codebase_search_handler()
    print("✓ Codebase search handler test passed")
    
    test_database_query_handler()
    print("✓ Database query handler test passed")
    
    test_tool_registry_execution()
    print("✓ Tool registry execution test passed")
    
    test_unknown_tool_execution()
    print("✓ Unknown tool execution test passed")
    
    test_tool_definitions_format()
    print("✓ Tool definitions format test passed")
    
    print("\nAll tests passed! MCP integration is working correctly.") 