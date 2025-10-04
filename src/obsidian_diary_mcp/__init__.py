"""Obsidian Diary MCP Server Package"""

from .server import mcp

__all__ = ["mcp"]


def main() -> None:
    """Run the MCP server."""
    mcp.run()
