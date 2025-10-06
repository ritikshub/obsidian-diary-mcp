#!/bin/bash
cd /Users/gps/Developer/obsidian-diary-mcp

mkdir -p logs

LOG_FILE="logs/server-$(date +%Y-%m-%d).log"

echo "Starting Obsidian Diary MCP Server...";
echo "Logs: $LOG_FILE"
echo "DIARY_PATH: ${DIARY_PATH:-default (~/Documents/diary)}"
echo "PLANNER_PATH: ${PLANNER_PATH:-default (~/Documents/planner)}"

# Export environment variables so they're available to Python
export DIARY_PATH
export PLANNER_PATH
export RECENT_ENTRIES_COUNT
export OLLAMA_URL
export OLLAMA_MODEL
export OLLAMA_TIMEOUT
export OLLAMA_TEMPERATURE
export OLLAMA_NUM_PREDICT

exec uv run obsidian-diary-mcp 2>&1 | tee -a "$LOG_FILE"