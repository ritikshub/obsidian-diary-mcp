# Obsidian Diary MCP Server

Smart journaling with AI-powered prompts and automatic backlinks for Obsidian.

**Features**: Dynamic reflection prompts • Smart backlinks • AI theme detection

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

## Daily Workflow

1. **Create today's entry**:
   ```bash
   copilot "create diary entry file"
   ```

2. **Write in Obsidian** - file created with AI-generated prompts based on recent entries

3. **Save with backlinks**:
   ```bash
   copilot "save diary entry with today's content"
   ```
   
4. **Backlinks appear automatically** - refresh Obsidian to see connections

**Other commands:**
```bash
copilot "list recent entries"
copilot "read diary entry for yesterday"
copilot "refresh all backlinks"
```

## How It Works

**AI Prompts**: Uses LLM sampling to analyze your recent entries and generate personalized reflection questions

**Smart Backlinks**: AI extracts themes from content to automatically link related entries with `[[YYYY-MM-DD]]` format

**No Hardcoded Content**: Everything is dynamically generated based on your actual writing patterns

## Tools Available

- `create_diary_template(date?)` - Generate template with AI prompts
- `create_diary_entry_file(date?)` - Create file with AI prompts
- `save_diary_entry(date, content)` - Save with auto-generated backlinks  
- `read_diary_entry(date)` - Read existing entry
- `list_recent_entries(count?)` - List recent entries
- `update_entry_backlinks(date)` - Refresh backlinks for one entry
- `refresh_all_backlinks()` - Refresh backlinks for all entries

## Configuration

```bash
export DIARY_PATH="/path/to/diary"           # Required
export RECENT_ENTRIES_COUNT=3                # How many recent entries to analyze for prompts
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

**License**: MIT • **Requirements**: Python 3.8+, FastMCP
