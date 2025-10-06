#!/bin/bash
cd /Users/gps/Developer/obsidian-diary-mcp

mkdir -p logs

LOG_FILE="logs/server-$(date +%Y-%m-%d).log"

echo "Starting Obsidian Diary MCP Server...";
echo "Logs: $LOG_FILE"
echo "DIARY_PATH: ${DIARY_PATH:-default (~/Documents/diary)}"
echo "PLANNER_PATH: ${PLANNER_PATH:-default (~/Documents/planner)}"

# Explicitly print all environment variables being passed
env | grep -E "DIARY_PATH|PLANNER_PATH|OLLAMA" >> "$LOG_FILE"

exec uv run obsidian-diary-mcp 2>&1 | tee -a "$LOG_FILE"