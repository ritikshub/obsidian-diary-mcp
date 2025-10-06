"""Configuration settings for the Obsidian Diary MCP server."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Load paths with debug info
diary_path_env = os.getenv("DIARY_PATH")
planner_path_env = os.getenv("PLANNER_PATH")

DIARY_PATH = Path(diary_path_env) if diary_path_env else Path.home() / "Documents" / "diary"
PLANNER_PATH = Path(planner_path_env) if planner_path_env else Path.home() / "Documents" / "planner"
RECENT_ENTRIES_COUNT = int(os.getenv("RECENT_ENTRIES_COUNT", "3"))

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:latest")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "30"))
OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.7"))
OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "200"))