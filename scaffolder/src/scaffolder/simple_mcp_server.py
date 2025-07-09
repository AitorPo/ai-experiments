"""
Simplified MCP Server implementation for file operations.
"""

import asyncio
import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server
from pydantic import BaseModel, Field

from .scaffolding import ProjectScaffolder


class FileOperationsMCPServer:
    """Simplified MCP Server for file operations."""

    def __init__(self):
        self.server = Server("file-operations-mcp")
        self.scaffolder = ProjectScaffolder()
        self._setup_handlers()

    def _setup_handlers(self):
        """Set up the MCP server handlers."""

        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """Return the list of available tools."""
            return [
                types.Tool(
                    name="create_folder",
                    description="Create a new folder at the specified location",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path where to create the folder"
                            },
                            "name": {
                                "type": "string",
                                "description": "Name of the folder to create"
                            },
                            "parents": {
                                "type": "boolean",
                                "description": "Create parent directories if they don't exist",
                                "default": True
                            }
                        },
                        "required": ["path", "name"]
                    }
                ),
                types.Tool(
                    name="create_file",
                    description="Create a new file with optional initial content",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path where to create the file"
                            },
                            "name": {
                                "type": "string",
                                "description": "Name of the file to create"
                            },
                            "content": {
                                "type": "string",
                                "description": "Initial content of the file",
                                "default": ""
                            },
                            "overwrite": {
                                "type": "boolean",
                                "description": "Overwrite if file exists",
                                "default": False
                            }
                        },
                        "required": ["path", "name"]
                    }
                ),
                types.Tool(
                    name="read_file",
                    description="Read the contents of a file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path of the file to read"
                            }
                        },
                        "required": ["path"]
                    }
                ),
                types.Tool(
                    name="write_file",
                    description="Write content to a file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path of the file to write"
                            },
                            "content": {
                                "type": "string",
                                "description": "Content to write to the file"
                            },
                            "append": {
                                "type": "boolean",
                                "description": "Append to file instead of overwriting",
                                "default": False
                            }
                        },
                        "required": ["path", "content"]
                    }
                ),
                types.Tool(
                    name="list_contents",
                    description="List contents of a directory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path of the directory to list"
                            },
                            "show_hidden": {
                                "type": "boolean",
                                "description": "Show hidden files and folders",
                                "default": False
                            }
                        },
                        "required": ["path"]
                    }
                ),
                types.Tool(
                    name="delete",
                    description="Delete a file or folder",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path of the file/folder to delete"
                            },
                            "recursive": {
                                "type": "boolean",
                                "description": "Delete recursively for folders",
                                "default": False
                            }
                        },
                        "required": ["path"]
                    }
                ),
                types.Tool(
                    name="move",
                    description="Move a file or folder to a new location",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "source_path": {
                                "type": "string",
                                "description": "Current path of the file/folder"
                            },
                            "destination_path": {
                                "type": "string",
                                "description": "Destination path"
                            },
                            "overwrite": {
                                "type": "boolean",
                                "description": "Overwrite if destination exists",
                                "default": False
                            }
                        },
                        "required": ["source_path", "destination_path"]
                    }
                ),
                types.Tool(
                    name="copy",
                    description="Copy a file or folder to a new location",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "source_path": {
                                "type": "string",
                                "description": "Source path to copy from"
                            },
                            "destination_path": {
                                "type": "string",
                                "description": "Destination path to copy to"
                            },
                            "overwrite": {
                                "type": "boolean",
                                "description": "Overwrite if destination exists",
                                "default": False
                            }
                        },
                        "required": ["source_path", "destination_path"]
                    }
                ),
                types.Tool(
                    name="rename",
                    description="Rename a file or folder",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "old_path": {
                                "type": "string",
                                "description": "Current path of the file/folder"
                            },
                            "new_name": {
                                "type": "string",
                                "description": "New name for the file/folder"
                            }
                        },
                        "required": ["old_path", "new_name"]
                    }
                ),
                types.Tool(
                    name="scaffold_project",
                    description="Scaffold a new project based on template and cursor rules",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_path": {
                                "type": "string",
                                "description": "Path where to create the project"
                            },
                            "project_name": {
                                "type": "string",
                                "description": "Name of the project"
                            },
                            "template_type": {
                                "type": "string",
                                "description": "Type of project template (python, fastapi, react, etc.)"
                            },
                            "cursor_rules": {
                                "type": "string",
                                "description": "Custom cursor rules for the project"
                            },
                            "module_name": {
                                "type": "string",
                                "description": "Name of the main module/entity for hexagonal architecture (e.g., 'user', 'product', 'order')"
                            }
                        },
                        "required": ["project_path", "project_name", "template_type", "module_name"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict[str, Any]
        ) -> Sequence[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            """Handle tool calls."""
            try:
                if name == "create_folder":
                    return await self._create_folder(arguments)
                elif name == "create_file":
                    return await self._create_file(arguments)
                elif name == "read_file":
                    return await self._read_file(arguments)
                elif name == "write_file":
                    return await self._write_file(arguments)
                elif name == "list_contents":
                    return await self._list_contents(arguments)
                elif name == "delete":
                    return await self._delete(arguments)
                elif name == "move":
                    return await self._move(arguments)
                elif name == "copy":
                    return await self._copy(arguments)
                elif name == "rename":
                    return await self._rename(arguments)
                elif name == "scaffold_project":
                    return await self._scaffold_project(arguments)
                else:
                    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
            except Exception as e:
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async def _create_folder(self, args: Dict[str, Any]) -> Sequence[types.TextContent]:
        """Create a new folder."""
        try:
            path = args["path"]
            name = args["name"]
            parents = args.get("parents", True)
            
            folder_path = Path(path) / name
            folder_path.mkdir(parents=parents, exist_ok=False)
            
            return [types.TextContent(
                type="text",
                text=f"Successfully created folder: {folder_path}"
            )]
        except FileExistsError:
            return [types.TextContent(
                type="text",
                text=f"Folder already exists: {folder_path}"
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Failed to create folder: {str(e)}"
            )]

    async def _create_file(self, args: Dict[str, Any]) -> Sequence[types.TextContent]:
        """Create a new file with optional content."""
        try:
            path = args["path"]
            name = args["name"]
            content = args.get("content", "")
            overwrite = args.get("overwrite", False)
            
            file_path = Path(path) / name
            
            if file_path.exists() and not overwrite:
                return [types.TextContent(
                    type="text",
                    text=f"File already exists: {file_path}. Use overwrite=true to replace."
                )]
            
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return [types.TextContent(
                type="text",
                text=f"Successfully created file: {file_path}"
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Failed to create file: {str(e)}"
            )]

    async def _read_file(self, args: Dict[str, Any]) -> Sequence[types.TextContent]:
        """Read the contents of a file."""
        try:
            path = Path(args["path"])
            
            if not path.exists():
                return [types.TextContent(
                    type="text",
                    text=f"File does not exist: {path}"
                )]
            
            if not path.is_file():
                return [types.TextContent(
                    type="text",
                    text=f"Path is not a file: {path}"
                )]
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return [types.TextContent(
                type="text",
                text=f"Contents of {path}:\n{content}"
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Failed to read file: {str(e)}"
            )]

    async def _write_file(self, args: Dict[str, Any]) -> Sequence[types.TextContent]:
        """Write content to a file."""
        try:
            path = Path(args["path"])
            content = args["content"]
            append = args.get("append", False)
            
            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            
            mode = 'a' if append else 'w'
            with open(path, mode, encoding='utf-8') as f:
                f.write(content)
            
            action = "appended to" if append else "written to"
            return [types.TextContent(
                type="text",
                text=f"Successfully {action} file: {path}"
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Failed to write file: {str(e)}"
            )]

    async def _list_contents(self, args: Dict[str, Any]) -> Sequence[types.TextContent]:
        """List contents of a directory."""
        try:
            path = Path(args["path"])
            show_hidden = args.get("show_hidden", False)
            
            if not path.exists():
                return [types.TextContent(
                    type="text",
                    text=f"Path does not exist: {path}"
                )]
            
            if not path.is_dir():
                return [types.TextContent(
                    type="text",
                    text=f"Path is not a directory: {path}"
                )]
            
            items = []
            for item in path.iterdir():
                if not show_hidden and item.name.startswith('.'):
                    continue
                
                item_type = "directory" if item.is_dir() else "file"
                items.append(f"{item_type}: {item.name}")
            
            contents = "\n".join(sorted(items))
            
            return [types.TextContent(
                type="text",
                text=f"Contents of {path}:\n{contents}"
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Failed to list contents: {str(e)}"
            )]

    async def _delete(self, args: Dict[str, Any]) -> Sequence[types.TextContent]:
        """Delete a file or folder."""
        try:
            path = Path(args["path"])
            recursive = args.get("recursive", False)
            
            if not path.exists():
                return [types.TextContent(
                    type="text",
                    text=f"Path does not exist: {path}"
                )]
            
            if path.is_dir():
                if recursive:
                    shutil.rmtree(path)
                else:
                    path.rmdir()  # Will fail if directory is not empty
            else:
                path.unlink()
            
            return [types.TextContent(
                type="text",
                text=f"Successfully deleted: {path}"
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Failed to delete: {str(e)}"
            )]

    async def _move(self, args: Dict[str, Any]) -> Sequence[types.TextContent]:
        """Move a file or folder to a new location."""
        try:
            source_path = Path(args["source_path"])
            dest_path = Path(args["destination_path"])
            overwrite = args.get("overwrite", False)
            
            if not source_path.exists():
                return [types.TextContent(
                    type="text",
                    text=f"Source path does not exist: {source_path}"
                )]
            
            if dest_path.exists() and not overwrite:
                return [types.TextContent(
                    type="text",
                    text=f"Destination already exists: {dest_path}. Use overwrite=true to replace."
                )]
            
            # Create parent directories if they don't exist
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            if overwrite and dest_path.exists():
                if dest_path.is_dir():
                    shutil.rmtree(dest_path)
                else:
                    dest_path.unlink()
            
            shutil.move(str(source_path), str(dest_path))
            
            return [types.TextContent(
                type="text",
                text=f"Successfully moved {source_path} to {dest_path}"
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Failed to move: {str(e)}"
            )]

    async def _copy(self, args: Dict[str, Any]) -> Sequence[types.TextContent]:
        """Copy a file or folder to a new location."""
        try:
            source_path = Path(args["source_path"])
            dest_path = Path(args["destination_path"])
            overwrite = args.get("overwrite", False)
            
            if not source_path.exists():
                return [types.TextContent(
                    type="text",
                    text=f"Source path does not exist: {source_path}"
                )]
            
            if dest_path.exists() and not overwrite:
                return [types.TextContent(
                    type="text",
                    text=f"Destination already exists: {dest_path}. Use overwrite=true to replace."
                )]
            
            # Create parent directories if they don't exist
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            if overwrite and dest_path.exists():
                if dest_path.is_dir():
                    shutil.rmtree(dest_path)
                else:
                    dest_path.unlink()
            
            if source_path.is_dir():
                shutil.copytree(source_path, dest_path)
            else:
                shutil.copy2(source_path, dest_path)
            
            return [types.TextContent(
                type="text",
                text=f"Successfully copied {source_path} to {dest_path}"
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Failed to copy: {str(e)}"
            )]

    async def _rename(self, args: Dict[str, Any]) -> Sequence[types.TextContent]:
        """Rename a file or folder."""
        try:
            old_path = Path(args["old_path"])
            new_name = args["new_name"]
            
            if not old_path.exists():
                return [types.TextContent(
                    type="text",
                    text=f"Source path does not exist: {old_path}"
                )]
            
            new_path = old_path.parent / new_name
            
            if new_path.exists():
                return [types.TextContent(
                    type="text",
                    text=f"Destination already exists: {new_path}"
                )]
            
            old_path.rename(new_path)
            
            return [types.TextContent(
                type="text",
                text=f"Successfully renamed {old_path} to {new_path}"
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Failed to rename: {str(e)}"
            )]

    async def _scaffold_project(self, args: Dict[str, Any]) -> Sequence[types.TextContent]:
        """Scaffold a new project based on template and cursor rules."""
        try:
            project_path = args["project_path"]
            project_name = args["project_name"]
            template_type = args["template_type"]
            cursor_rules = args.get("cursor_rules")
            module_name = args.get("module_name")
            
            result = await self.scaffolder.scaffold_project(
                project_path=project_path,
                project_name=project_name,
                template_type=template_type,
                cursor_rules=cursor_rules,
                module_name=module_name
            )
            
            return [types.TextContent(
                type="text",
                text=result
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Failed to scaffold project: {str(e)}"
            )]

    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, 
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point for the MCP server."""
    server = FileOperationsMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main()) 