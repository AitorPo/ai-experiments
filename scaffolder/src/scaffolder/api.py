"""
FastAPI wrapper for the MCP file operations server.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import asyncio
import json
from mcp.types import ListToolsRequest

from .simple_mcp_server import FileOperationsMCPServer


app = FastAPI(
    title="File Operations MCP Server",
    description="REST API wrapper for MCP file operations server",
    version="0.1.0"
)

# Initialize the MCP server
mcp_server = FileOperationsMCPServer()


# Pydantic models for API requests
class CreateFolderRequest(BaseModel):
    path: str = Field(description="Path where to create the folder")
    name: str = Field(description="Name of the folder to create")
    parents: bool = Field(default=True, description="Create parent directories if they don't exist")


class CreateFileRequest(BaseModel):
    path: str = Field(description="Path where to create the file")
    name: str = Field(description="Name of the file to create")
    content: str = Field(default="", description="Initial content of the file")
    overwrite: bool = Field(default=False, description="Overwrite if file exists")


class RenameRequest(BaseModel):
    old_path: str = Field(description="Current path of the file/folder")
    new_name: str = Field(description="New name for the file/folder")


class MoveRequest(BaseModel):
    source_path: str = Field(description="Current path of the file/folder")
    destination_path: str = Field(description="Destination path")
    overwrite: bool = Field(default=False, description="Overwrite if destination exists")


class DeleteRequest(BaseModel):
    path: str = Field(description="Path of the file/folder to delete")
    recursive: bool = Field(default=False, description="Delete recursively for folders")


class ListContentsRequest(BaseModel):
    path: str = Field(description="Path of the directory to list")
    show_hidden: bool = Field(default=False, description="Show hidden files and folders")


class ReadFileRequest(BaseModel):
    path: str = Field(description="Path of the file to read")


class WriteFileRequest(BaseModel):
    path: str = Field(description="Path of the file to write")
    content: str = Field(description="Content to write to the file")
    append: bool = Field(default=False, description="Append to file instead of overwriting")


class CopyRequest(BaseModel):
    source_path: str = Field(description="Source path to copy from")
    destination_path: str = Field(description="Destination path to copy to")
    overwrite: bool = Field(default=False, description="Overwrite if destination exists")


class ScaffoldProjectRequest(BaseModel):
    project_path: str = Field(description="Path where to create the project")
    project_name: str = Field(description="Name of the project")
    template_type: str = Field(description="Type of project template (python, fastapi, react, etc.)")
    cursor_rules: Optional[str] = Field(default=None, description="Custom cursor rules for the project")
    module_name: Optional[str] = Field(default=None, description="Name of the main module/entity for hexagonal architecture (e.g., 'user', 'product', 'order')")


class ToolResponse(BaseModel):
    success: bool
    message: str
    error: Optional[str] = None


def get_tool_methods():
    """Get the mapping of tool names to server methods."""
    return {
        "create_folder": mcp_server._create_folder,
        "create_file": mcp_server._create_file,
        "read_file": mcp_server._read_file,
        "write_file": mcp_server._write_file,
        "list_contents": mcp_server._list_contents,
        "delete": mcp_server._delete,
        "move": mcp_server._move,
        "copy": mcp_server._copy,
        "rename": mcp_server._rename,
        "scaffold_project": mcp_server._scaffold_project,
    }


async def call_mcp_tool(tool_name: str, arguments: Dict[str, Any]) -> ToolResponse:
    """Call an MCP tool method directly."""
    try:
        tool_methods = get_tool_methods()
        
        if tool_name not in tool_methods:
            return ToolResponse(
                success=False,
                message="",
                error=f"Unknown tool: {tool_name}"
            )
        
        # Call the method directly
        result = await tool_methods[tool_name](arguments)
        
        # Extract the text from the result
        if result and len(result) > 0:
            message = result[0].text
            return ToolResponse(
                success=True,
                message=message,
                error=None
            )
        else:
            return ToolResponse(
                success=True,
                message="Operation completed successfully",
                error=None
            )
            
    except Exception as e:
        return ToolResponse(
            success=False,
            message="",
            error=str(e)
        )


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "File Operations MCP Server API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


async def get_tools_from_mcp_server():
    """Get tools dynamically from the MCP server."""
    try:
        # Access the list_tools handler directly from the server
        # The handler is stored in the server's request_handlers
        for handler_name, handler_func in mcp_server.server.request_handlers.items():
            if handler_name == ListToolsRequest:
                # Call the handler function with a properly constructed ListToolsRequest
                request = ListToolsRequest(method="tools/list", params=None)
                result = await handler_func(request)
                
                # The result is a ServerResult, need to access the root attribute
                if hasattr(result, 'root') and hasattr(result.root, 'tools'):
                    mcp_tools = result.root.tools
                    # Convert MCP Tool objects to our API format
                    tools = []
                    for tool in mcp_tools:
                        tools.append({
                            "name": getattr(tool, 'name', 'unknown'),
                            "description": getattr(tool, 'description', 'No description'),
                            "schema": getattr(tool, 'inputSchema', {})
                        })
                    return tools
                else:
                    return []
        
        # Fallback: if handler not found, return empty list
        return []
        
    except Exception as e:
        # If something goes wrong, return empty list and let the main function handle fallback
        return []


@app.get("/tools")
async def list_tools():
    """List all available MCP tools with their schemas."""
    try:
        tools = await get_tools_from_mcp_server()
        if tools:
            return {"tools": tools}
        else:
            # Fallback if no tools retrieved from MCP server
            tool_methods = get_tool_methods()
            fallback_tools = [{"name": name, "description": f"Tool: {name}", "schema": {}} for name in tool_methods.keys()]
            return {"tools": fallback_tools}
    except Exception as e:
        # Emergency fallback
        tool_methods = get_tool_methods()
        tools = [{"name": name, "description": f"Tool: {name}", "schema": {}} for name in tool_methods.keys()]
        return {"tools": tools, "error": str(e)}


@app.post("/tools/create_folder", response_model=ToolResponse)
async def create_folder(request: CreateFolderRequest):
    """Create a new folder."""
    return await call_mcp_tool("create_folder", request.model_dump())


@app.post("/tools/create_file", response_model=ToolResponse)
async def create_file(request: CreateFileRequest):
    """Create a new file with optional content."""
    return await call_mcp_tool("create_file", request.model_dump())


@app.post("/tools/rename", response_model=ToolResponse)
async def rename(request: RenameRequest):
    """Rename a file or folder."""
    return await call_mcp_tool("rename", request.model_dump())


@app.post("/tools/move", response_model=ToolResponse)
async def move(request: MoveRequest):
    """Move a file or folder to a new location."""
    return await call_mcp_tool("move", request.model_dump())


@app.post("/tools/delete", response_model=ToolResponse)
async def delete(request: DeleteRequest):
    """Delete a file or folder."""
    return await call_mcp_tool("delete", request.model_dump())


@app.post("/tools/list_contents", response_model=ToolResponse)
async def list_contents(request: ListContentsRequest):
    """List contents of a directory."""
    return await call_mcp_tool("list_contents", request.model_dump())


@app.post("/tools/read_file", response_model=ToolResponse)
async def read_file(request: ReadFileRequest):
    """Read the contents of a file."""
    return await call_mcp_tool("read_file", request.model_dump())


@app.post("/tools/write_file", response_model=ToolResponse)
async def write_file(request: WriteFileRequest):
    """Write content to a file."""
    return await call_mcp_tool("write_file", request.model_dump())


@app.post("/tools/copy", response_model=ToolResponse)
async def copy(request: CopyRequest):
    """Copy a file or folder to a new location."""
    return await call_mcp_tool("copy", request.model_dump())


@app.post("/tools/scaffold_project", response_model=ToolResponse)
async def scaffold_project(request: ScaffoldProjectRequest):
    """Scaffold a new project based on template and cursor rules."""
    return await call_mcp_tool("scaffold_project", request.model_dump())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)