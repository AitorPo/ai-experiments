#!/usr/bin/env python3
"""
Main entry point for the File Operations MCP Server.

This can run either as:
1. MCP server (stdio transport)
2. FastAPI REST API server
"""

import asyncio
import sys
import argparse
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from scaffolder.simple_mcp_server import FileOperationsMCPServer

async def run_mcp_server():
    """Run the MCP server with stdio transport."""
    server = FileOperationsMCPServer()
    await server.run()


def run_fastapi_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the FastAPI REST API server."""
    try:
        from scaffolder.api import app
        import uvicorn
        uvicorn.run(app, host=host, port=port)
    except ImportError as e:
        print(f"Error importing FastAPI components: {e}")
        print("Make sure all dependencies are installed: uv pip install -e .")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="File Operations MCP Server")
    parser.add_argument(
        "--mode",
        choices=["mcp", "api"],
        default="mcp",
        help="Run mode: 'mcp' for MCP server, 'api' for FastAPI server"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind FastAPI server to (only for api mode)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind FastAPI server to (only for api mode)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "mcp":
        print("Starting MCP server with stdio transport...", file=sys.stderr)
        asyncio.run(run_mcp_server())
    elif args.mode == "api":
        print(f"Starting FastAPI server on {args.host}:{args.port}...", file=sys.stderr)
        run_fastapi_server(args.host, args.port)


if __name__ == "__main__":
    main() 