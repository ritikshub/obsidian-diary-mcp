"""Obsidian Diary MCP Server Package

A modular diary management system with AI-powered analysis and Obsidian integration.
"""

from .server import mcp
from .config import DIARY_PATH, OLLAMA_URL, OLLAMA_MODEL
from .entry_manager import entry_manager
from .analysis import analysis_engine
from .template_generator import template_generator
from .ollama_client import ollama_client

__all__ = [
    "mcp",
    "DIARY_PATH", 
    "OLLAMA_URL", 
    "OLLAMA_MODEL",
    "entry_manager",
    "analysis_engine", 
    "template_generator",
    "ollama_client"
]


def main() -> None:
    """Run the MCP server."""
    mcp.run()
