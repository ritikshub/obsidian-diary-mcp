# Obsidian Diary MCP Server

Smart journaling with AI-powered prompts and automatic backlinks for Obsidian.

**Features**: Dynamic reflection prompts • Smart backlinks • Adaptive templates • Theme detection

## Quick Start

```bash
# Install
uv sync

# Configure diary path
export DIARY_PATH="/path/to/your/diary"

# Run
uv run fastmcp run src/obsidian_diary_mcp/server.py
```

## GitHub Copilot CLI Setup

```bash
/mcp add
```
- **Name**: `obsidian-diary`
- **Command**: `uv run fastmcp run src/obsidian_diary_mcp/server.py`  
- **Working Directory**: `/path/to/this/repo`
- **Environment**: `{"DIARY_PATH": "/path/to/your/diary"}`

Then use naturally:
```bash
gh copilot chat "create a diary template for today"
gh copilot chat "help me journal about my day"
```

## How It Works

**Dynamic Prompts**: Analyzes your recent entries to generate personalized reflection questions (no hardcoded categories)

**Smart Backlinks**: Uses content similarity to automatically link related entries with `[[YYYY-MM-DD]]` format

**Adaptive**: Learns from your writing patterns and vocabulary over time

## Tools Available

- `create_diary_template(date?)` - Generate template with dynamic prompts
- `save_diary_entry(date, content)` - Save with auto-generated backlinks  
- `read_diary_entry(date)` - Read existing entry
- `list_recent_entries(count?)` - List recent entries
- `update_entry_backlinks(date)` - Refresh backlinks

## Configuration

```bash
export DIARY_PATH="/path/to/diary"           # Required
export RECENT_ENTRIES_COUNT=3                # How many recent entries to analyze
export MAX_THEMES=15                         # Max themes per analysis
export MIN_THEME_FREQUENCY=1                 # Min word frequency for themes
```

## Entry Format

Files: `YYYY-MM-DD.md` in your diary directory

```markdown
# Thursday, October 3, 2024

## 🤔 Reflection Prompts
**How did work play out today?**

## 💭 Brain Dump
Your thoughts...

---
**Related entries:** [[2024-09-28]], [[2024-09-30]]
```

## Other MCP Clients

Works with Claude Desktop and other MCP-compatible tools. See [MCP documentation](https://modelcontextprotocol.io/) for setup.

## Non-English Support

Update the `stop_words` set in `extract_themes_and_topics()` for your language.

**License**: MIT • **Requirements**: Python 3.8+, FastMCP
