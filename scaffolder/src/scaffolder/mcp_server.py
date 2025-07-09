"""
MCP Server implementation for file operations and project scaffolding.
"""

import asyncio
import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    INVALID_PARAMS,
    CallToolResult,
    ListToolsResult,
    Tool,
    TextContent,
)
from pydantic import BaseModel, Field


class FileOperationError(Exception):
    """Custom exception for file operation errors."""
    pass


class CreateFolderArgs(BaseModel):
    """Arguments for creating a folder."""
    path: str = Field(description="Path where to create the folder")
    name: str = Field(description="Name of the folder to create")
    parents: bool = Field(default=True, description="Create parent directories if they don't exist")


class CreateFileArgs(BaseModel):
    """Arguments for creating a file."""
    path: str = Field(description="Path where to create the file")
    name: str = Field(description="Name of the file to create")
    content: str = Field(default="", description="Initial content of the file")
    overwrite: bool = Field(default=False, description="Overwrite if file exists")


class RenameArgs(BaseModel):
    """Arguments for renaming a file or folder."""
    old_path: str = Field(description="Current path of the file/folder")
    new_name: str = Field(description="New name for the file/folder")


class MoveArgs(BaseModel):
    """Arguments for moving a file or folder."""
    source_path: str = Field(description="Current path of the file/folder")
    destination_path: str = Field(description="Destination path")
    overwrite: bool = Field(default=False, description="Overwrite if destination exists")


class DeleteArgs(BaseModel):
    """Arguments for deleting a file or folder."""
    path: str = Field(description="Path of the file/folder to delete")
    recursive: bool = Field(default=False, description="Delete recursively for folders")


class ListContentsArgs(BaseModel):
    """Arguments for listing directory contents."""
    path: str = Field(description="Path of the directory to list")
    show_hidden: bool = Field(default=False, description="Show hidden files and folders")


class ReadFileArgs(BaseModel):
    """Arguments for reading a file."""
    path: str = Field(description="Path of the file to read")


class WriteFileArgs(BaseModel):
    """Arguments for writing to a file."""
    path: str = Field(description="Path of the file to write")
    content: str = Field(description="Content to write to the file")
    append: bool = Field(default=False, description="Append to file instead of overwriting")


class CopyArgs(BaseModel):
    """Arguments for copying a file or folder."""
    source_path: str = Field(description="Source path to copy from")
    destination_path: str = Field(description="Destination path to copy to")
    overwrite: bool = Field(default=False, description="Overwrite if destination exists")


class ScaffoldProjectArgs(BaseModel):
    """Arguments for scaffolding a project."""
    project_path: str = Field(description="Path where to create the project")
    project_name: str = Field(description="Name of the project")
    template_type: str = Field(description="Type of project template (python, fastapi, react, etc.)")
    cursor_rules: Optional[str] = Field(default=None, description="Custom cursor rules for the project")
    module_name: Optional[str] = Field(default=None, description="Name of the main module/entity for hexagonal architecture (e.g., 'user', 'product', 'order')")


class FileOperationsMCPServer:
    """MCP Server for file operations and project scaffolding."""

    def __init__(self):
        self.server = Server("file-operations-mcp")
        self._setup_tools()

    def _setup_tools(self):
        """Setup all available tools for the MCP server."""
        
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """List all available tools."""
            tools = [
                Tool(
                    name="create_folder",
                    description="Create a new folder at the specified location",
                    inputSchema=CreateFolderArgs.model_json_schema(),
                ),
                Tool(
                    name="create_file",
                    description="Create a new file with optional initial content",
                    inputSchema=CreateFileArgs.model_json_schema(),
                ),
                Tool(
                    name="rename",
                    description="Rename a file or folder",
                    inputSchema=RenameArgs.model_json_schema(),
                ),
                Tool(
                    name="move",
                    description="Move a file or folder to a new location",
                    inputSchema=MoveArgs.model_json_schema(),
                ),
                Tool(
                    name="delete",
                    description="Delete a file or folder",
                    inputSchema=DeleteArgs.model_json_schema(),
                ),
                Tool(
                    name="list_contents",
                    description="List contents of a directory",
                    inputSchema=ListContentsArgs.model_json_schema(),
                ),
                Tool(
                    name="read_file",
                    description="Read the contents of a file",
                    inputSchema=ReadFileArgs.model_json_schema(),
                ),
                Tool(
                    name="write_file",
                    description="Write content to a file",
                    inputSchema=WriteFileArgs.model_json_schema(),
                ),
                Tool(
                    name="copy",
                    description="Copy a file or folder to a new location",
                    inputSchema=CopyArgs.model_json_schema(),
                ),
                Tool(
                    name="scaffold_project",
                    description="Scaffold a new project based on template and cursor rules",
                    inputSchema=ScaffoldProjectArgs.model_json_schema(),
                ),
            ]
            return ListToolsResult(tools=tools)

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Call a specific tool with the given arguments."""
            try:
                if name == "create_folder":
                    return await self._create_folder(CreateFolderArgs(**arguments))
                elif name == "create_file":
                    return await self._create_file(CreateFileArgs(**arguments))
                elif name == "rename":
                    return await self._rename(RenameArgs(**arguments))
                elif name == "move":
                    return await self._move(MoveArgs(**arguments))
                elif name == "delete":
                    return await self._delete(DeleteArgs(**arguments))
                elif name == "list_contents":
                    return await self._list_contents(ListContentsArgs(**arguments))
                elif name == "read_file":
                    return await self._read_file(ReadFileArgs(**arguments))
                elif name == "write_file":
                    return await self._write_file(WriteFileArgs(**arguments))
                elif name == "copy":
                    return await self._copy(CopyArgs(**arguments))
                elif name == "scaffold_project":
                    return await self._scaffold_project(ScaffoldProjectArgs(**arguments))
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Unknown tool: {name}")],
                        isError=True,
                    )
            except Exception as e:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")],
                    isError=True,
                )

    async def _create_folder(self, args: CreateFolderArgs) -> CallToolResult:
        """Create a new folder."""
        try:
            folder_path = Path(args.path) / args.name
            folder_path.mkdir(parents=args.parents, exist_ok=False)
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Successfully created folder: {folder_path}"
                )]
            )
        except FileExistsError:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Folder already exists: {folder_path}"
                )],
                isError=True,
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Failed to create folder: {str(e)}"
                )],
                isError=True,
            )

    async def _create_file(self, args: CreateFileArgs) -> CallToolResult:
        """Create a new file with optional content."""
        try:
            file_path = Path(args.path) / args.name
            
            if file_path.exists() and not args.overwrite:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"File already exists: {file_path}. Use overwrite=true to replace."
                    )],
                    isError=True,
                )
            
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(args.content)
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Successfully created file: {file_path}"
                )]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Failed to create file: {str(e)}"
                )],
                isError=True,
            )

    async def _rename(self, args: RenameArgs) -> CallToolResult:
        """Rename a file or folder."""
        try:
            old_path = Path(args.old_path)
            new_path = old_path.parent / args.new_name
            
            if not old_path.exists():
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Source path does not exist: {old_path}"
                    )],
                    isError=True,
                )
            
            if new_path.exists():
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Destination already exists: {new_path}"
                    )],
                    isError=True,
                )
            
            old_path.rename(new_path)
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Successfully renamed {old_path} to {new_path}"
                )]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Failed to rename: {str(e)}"
                )],
                isError=True,
            )

    async def _move(self, args: MoveArgs) -> CallToolResult:
        """Move a file or folder to a new location."""
        try:
            source_path = Path(args.source_path)
            dest_path = Path(args.destination_path)
            
            if not source_path.exists():
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Source path does not exist: {source_path}"
                    )],
                    isError=True,
                )
            
            if dest_path.exists() and not args.overwrite:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Destination already exists: {dest_path}. Use overwrite=true to replace."
                    )],
                    isError=True,
                )
            
            # Create parent directories if they don't exist
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            if args.overwrite and dest_path.exists():
                if dest_path.is_dir():
                    shutil.rmtree(dest_path)
                else:
                    dest_path.unlink()
            
            shutil.move(str(source_path), str(dest_path))
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Successfully moved {source_path} to {dest_path}"
                )]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Failed to move: {str(e)}"
                )],
                isError=True,
            )

    async def _delete(self, args: DeleteArgs) -> CallToolResult:
        """Delete a file or folder."""
        try:
            path = Path(args.path)
            
            if not path.exists():
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Path does not exist: {path}"
                    )],
                    isError=True,
                )
            
            if path.is_dir():
                if args.recursive:
                    shutil.rmtree(path)
                else:
                    path.rmdir()  # Will fail if directory is not empty
            else:
                path.unlink()
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Successfully deleted: {path}"
                )]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Failed to delete: {str(e)}"
                )],
                isError=True,
            )

    async def _list_contents(self, args: ListContentsArgs) -> CallToolResult:
        """List contents of a directory."""
        try:
            path = Path(args.path)
            
            if not path.exists():
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Path does not exist: {path}"
                    )],
                    isError=True,
                )
            
            if not path.is_dir():
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Path is not a directory: {path}"
                    )],
                    isError=True,
                )
            
            items = []
            for item in path.iterdir():
                if not args.show_hidden and item.name.startswith('.'):
                    continue
                
                item_type = "directory" if item.is_dir() else "file"
                items.append(f"{item_type}: {item.name}")
            
            contents = "\n".join(sorted(items))
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Contents of {path}:\n{contents}"
                )]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Failed to list contents: {str(e)}"
                )],
                isError=True,
            )

    async def _read_file(self, args: ReadFileArgs) -> CallToolResult:
        """Read the contents of a file."""
        try:
            path = Path(args.path)
            
            if not path.exists():
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"File does not exist: {path}"
                    )],
                    isError=True,
                )
            
            if not path.is_file():
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Path is not a file: {path}"
                    )],
                    isError=True,
                )
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Contents of {path}:\n{content}"
                )]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Failed to read file: {str(e)}"
                )],
                isError=True,
            )

    async def _write_file(self, args: WriteFileArgs) -> CallToolResult:
        """Write content to a file."""
        try:
            path = Path(args.path)
            
            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            
            mode = 'a' if args.append else 'w'
            with open(path, mode, encoding='utf-8') as f:
                f.write(args.content)
            
            action = "appended to" if args.append else "written to"
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Successfully {action} file: {path}"
                )]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Failed to write file: {str(e)}"
                )],
                isError=True,
            )

    async def _copy(self, args: CopyArgs) -> CallToolResult:
        """Copy a file or folder to a new location."""
        try:
            source_path = Path(args.source_path)
            dest_path = Path(args.destination_path)
            
            if not source_path.exists():
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Source path does not exist: {source_path}"
                    )],
                    isError=True,
                )
            
            if dest_path.exists() and not args.overwrite:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Destination already exists: {dest_path}. Use overwrite=true to replace."
                    )],
                    isError=True,
                )
            
            # Create parent directories if they don't exist
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            if args.overwrite and dest_path.exists():
                if dest_path.is_dir():
                    shutil.rmtree(dest_path)
                else:
                    dest_path.unlink()
            
            if source_path.is_dir():
                shutil.copytree(source_path, dest_path)
            else:
                shutil.copy2(source_path, dest_path)
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Successfully copied {source_path} to {dest_path}"
                )]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Failed to copy: {str(e)}"
                )],
                isError=True,
            )

    async def _scaffold_project(self, args: ScaffoldProjectArgs) -> CallToolResult:
        """Scaffold a new project based on template and cursor rules."""
        try:
            from scaffolder.scaffolding import ProjectScaffolder
            
            scaffolder = ProjectScaffolder()
            result = await scaffolder.scaffold_project(
                project_path=args.project_path,
                project_name=args.project_name,
                template_type=args.template_type,
                cursor_rules=args.cursor_rules,
                module_name=args.module_name
            )
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=result
                )]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Failed to scaffold project: {str(e)}"
                )],
                isError=True,
            )

    async def run(self, transport_type: str = "stdio"):
        """Run the MCP server."""
        if transport_type == "stdio":
            from mcp.server.stdio import stdio_server
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="file-operations-mcp",
                        server_version="0.1.0",
                        capabilities=self.server.get_capabilities(
                            notification_options=None,
                            experimental_capabilities=None,
                        ),
                    ),
                )
        else:
            raise ValueError(f"Unsupported transport type: {transport_type}")


async def main():
    """Main entry point for the MCP server."""
    server = FileOperationsMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main()) 