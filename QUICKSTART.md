# Quick Start Guide

## What You Got

An MCP (Model Context Protocol) server that makes your Obsidian diary journaling smarter with:

✨ **Smart Templates** - Creates personalized diary templates by analyzing your recent entries and generating contextual reflection prompts

🔗 **Auto-Tagging** - Automatically finds and adds relevant backlinks to related diary entries using content similarity

## Installation Complete

Everything is already set up in `/Users/gps/Documents/diary/obsidian-diary-mcp`

## Test It Right Now

### Option 1: Run the Demo
```bash
cd /Users/gps/Documents/diary/obsidian-diary-mcp
uv run python demo.py
```

This shows you:
- Theme detection from your entries
- How templates are generated
- How auto-tagging works

### Option 2: Interactive Testing (Recommended)
```bash
cd /Users/gps/Documents/diary/obsidian-diary-mcp
uv run fastmcp dev src/obsidian_diary_mcp/server.py
```

This opens a web interface where you can:
1. Try `create_diary_template()` - Generate a template for today
2. Try `list_recent_entries()` - See your diary history
3. Try `read_diary_entry(date="2025-10-03")` - Read an entry
4. Try `save_diary_entry(date="2025-10-04", content="...")` - Save with auto-links

## Available Tools

### 🎯 `create_diary_template(date?)`
Creates a personalized template with:
- Links to your 3 most recent entries
- Contextual reflection prompts based on your themes
- Brain dump section
- Placeholder for auto-generated backlinks

**Example:** `create_diary_template()` or `create_diary_template(date="2025-10-04")`

### 💾 `save_diary_entry(date, content)`
Saves your entry and automatically adds relevant backlinks based on content similarity.

**Example:** `save_diary_entry(date="2025-10-04", content="Today I worked on Python...")`

### 📖 `read_diary_entry(date)`
Reads an existing diary entry.

**Example:** `read_diary_entry(date="2025-10-03")`

### 📋 `list_recent_entries(count?)`
Lists your recent diary entries.

**Example:** `list_recent_entries(count=5)`

### 🔄 `update_entry_backlinks(date)`
Re-analyzes an existing entry and updates its backlinks.

**Example:** `update_entry_backlinks(date="2025-10-03")`

## Use with Claude Desktop

See `CLAUDE_CONFIG.md` for detailed setup instructions.

Quick version:
1. Edit `~/Library/Application Support/Claude/claude_desktop_config.json`
2. Add the configuration from `CLAUDE_CONFIG.md`
3. Restart Claude Desktop
4. Ask Claude: "Create a diary template for today"

## How It's Smart

**Theme Detection**: Analyzes your entries to identify recurring topics (work, health, relationships, learning, emotions) and generates appropriate reflection prompts.

**Backlink Generation**: Uses Jaccard similarity to compare themes across all your entries and automatically links related content.

**Context-Aware Prompts**: If you've been writing about:
- Work/coding → Asks about technical progress
- Health/exercise → Asks about physical wellbeing
- People/relationships → Asks about connections
- Learning/reading → Asks about knowledge building
- Emotions → Prompts emotional awareness

## Example Workflow

1. **Morning**: Ask the MCP to create today's template
   - Shows your recent entries
   - Gives you prompts based on your recent themes
   
2. **Throughout the day**: Fill in the template in Obsidian

3. **Evening**: Save your entry
   - MCP automatically finds related past entries
   - Adds backlinks in Obsidian format

4. **Later**: Update backlinks on old entries as you add more content
   - Keeps your knowledge graph connected

## File Structure

```
obsidian-diary-mcp/
├── src/
│   └── obsidian_diary_mcp/
│       ├── __init__.py
│       └── server.py          # Main MCP server implementation
├── README.md                  # Full documentation
├── CLAUDE_CONFIG.md          # Claude Desktop setup
├── QUICKSTART.md             # This file
├── demo.py                   # Interactive demo
└── pyproject.toml            # Project config
```

## Need Help?

- Full docs: See `README.md`
- Claude setup: See `CLAUDE_CONFIG.md`
- Issues: The diary path is hardcoded to `/Users/gps/Documents/diary`
  - To change it, edit `DIARY_PATH` in `src/obsidian_diary_mcp/server.py`

## What's Next?

1. Try the interactive demo to see it in action
2. Configure Claude Desktop to use it daily
3. Start journaling with AI-powered reflection prompts
4. Watch your Obsidian vault build a rich knowledge graph automatically

Happy journaling! 📝✨
