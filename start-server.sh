#!/usr/bin/env bash
# --------------------------------------------
# MCP Server Starter for Claude + Ollama
# Windows + Git Bash safe
# --------------------------------------------

# Navigate to project root
cd "/c/Users/Ritik Roushan/Desktop/obsidian-diary-mcp" || exit 1

# Python UTF-8 environment
export PYTHONIOENCODING=utf-8
export PYTHONUTF8=1
export LANG=C.UTF-8
export LC_ALL=C.UTF-8

# Environment variables from Claude Desktop (or fallback defaults)
export DIARY_PATH="${DIARY_PATH:-/c/Users/Ritik Roushan/Documents/Obsidian Vault}"
export OLLAMA_URL="${OLLAMA_URL:-http://localhost:11434}"
export OLLAMA_MODEL="${OLLAMA_MODEL:-gemma3:1b}"
export OLLAMA_TIMEOUT="${OLLAMA_TIMEOUT:-30}"
export OLLAMA_TEMPERATURE="${OLLAMA_TEMPERATURE:-0.7}"
export OLLAMA_NUM_PREDICT="${OLLAMA_NUM_PREDICT:-200}"

echo "----------------------------------------"
echo "Starting Obsidian Diary MCP Server..."
echo "DIARY_PATH = $DIARY_PATH"
echo "OLLAMA_URL = $OLLAMA_URL"
echo "OLLAMA_MODEL = $OLLAMA_MODEL"
echo "OLLAMA_TIMEOUT = $OLLAMA_TIMEOUT"
echo "OLLAMA_TEMPERATURE = $OLLAMA_TEMPERATURE"
echo "OLLAMA_NUM_PREDICT = $OLLAMA_NUM_PREDICT"
echo "----------------------------------------"

# Run server.py as a module to fix relative imports
uv run -m src.obsidian_diary_mcp.server
