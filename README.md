# Obsidian Diary MCP Server

Sophisticated cognitive journaling with AI philosopher-generated prompts and automatic memory linking for Obsidian.

**Features**: Intellectually rigorous analysis prompts • Automatic memory links • Cognitive pattern detection

## Quick Start

```bash
# Install
cd /path/to/obsidian-diary-mcp
uv sync

# Make start script executable
chmod +x start-server.sh

# Configure diary path
export DIARY_PATH="/path/to/your/diary"

# Run (for testing)
./start-server.sh
```

## GitHub Copilot CLI Setup

1. **Install Copilot CLI**:
   ```bash
   npm install -g @github/copilot
   ```

2. **Launch Copilot CLI**:
   ```bash
   copilot
   ```

3. **Add the MCP server**:
   ```bash
   /mcp add
   ```
   
   Fill in the form:
   - **Name**: `diary`
   - **Command**: `/Users/gps/Developer/obsidian-diary-mcp/start-server.sh`
   - **Args**: (leave empty)
   - **Environment**: `DIARY_PATH=/Users/gps/Documents/diary`

4. **Save with Ctrl+S**

5. **Verify setup**:
   ```bash
   cat ~/.copilot/mcp-config.json
   ```
   Should show your obsidian-diary server configuration.

The MCP server config is stored in `~/.copilot/mcp-config.json`

**Working Configuration Example:**
```json
{
  "mcpServers": {
    "diary": {
      "type": "local",
      "command": "/Users/gps/Developer/obsidian-diary-mcp/start-server.sh",
      "args": [],
      "tools": ["*"],
      "env": {
        "DIARY_PATH": "/Users/gps/Documents/diary"
      }
    }
  }
}
```

## Daily Workflow

1. **Create sophisticated entry**:
   ```bash
   copilot "use create_diary_entry_file to make today's intellectual journal"
   ```
   
   **Or with analytical focus**:
   ```bash
   copilot "create an entry focused on current struggles"
   copilot "create an entry focused on cognitive patterns"  
   copilot "create an entry focused on decision frameworks"
   ```

2. **Deep analysis in Obsidian** - explore sophisticated prompts designed by AI philosopher

3. **Complete when done**:
   ```bash
   copilot "ok done with today's entry" 
   # OR
   copilot "use complete_diary_entry to finalize with automatic memory links"
   ```
   
4. **Memory links auto-generated** - cognitive themes analyzed and connections made automatically

**Other commands:**
```bash
copilot "use list_recent_entries to show my recent journal entries"
copilot "use read_diary_entry to read yesterday's entry"
copilot "ok done with today's entry"  # Auto-complete with memory links
copilot "use refresh_all_backlinks to update all entry connections"
```

## Troubleshooting

**MCP server not found?**
1. Check if the server is in your MCP config: `cat ~/.copilot/mcp-config.json`
2. Restart Copilot CLI after adding the MCP server
3. Make sure the start script is executable: `chmod +x start-server.sh`
4. Test the server manually: `./start-server.sh`

**Tools not working?**
- Be explicit: `"use create_diary_entry_file tool"`
- Check available tools: Ask Copilot `"what MCP tools are available?"`
- Verify DIARY_PATH environment variable is set correctly

## How It Works

**AI Prompts**: Uses LLM sampling to analyze your recent entries and generate personalized reflection questions

**Obsidian-Integrated Memory Links**: AI analyzes cognitive themes to create `[[YYYY-MM-DD]]` backlinks that integrate seamlessly with Obsidian's backlink system. View your intellectual network in the Backlinks panel!

**No Hardcoded Content**: Everything is dynamically generated based on your actual writing patterns

## Tools Available

- `create_diary_template(date?, focus?)` - Generate sophisticated template with intellectually rigorous prompts
- `create_diary_entry_file(date?, focus?)` - Create file with AI philosopher-generated analytical prompts
- `complete_diary_entry(date?)` - **NEW**: Auto-generate memory links and cognitive summary when done writing
- `save_diary_entry(date, content)` - Save with auto-generated backlinks  
- `read_diary_entry(date)` - Read existing entry
- `list_recent_entries(count?)` - List recent entries
- `update_entry_backlinks(date)` - Refresh backlinks for one entry
- `refresh_all_backlinks()` - Refresh backlinks for all entries

## Configuration

```bash
export DIARY_PATH="/path/to/diary"           # Required
export RECENT_ENTRIES_COUNT=3                # How many recent entries to analyze for prompts

# Optional: For AI-powered prompts with Ollama
export OLLAMA_MODEL=\"llama3.1:latest\"       # Ollama model (default: llama3.1:latest)
export OLLAMA_URL=\"http://localhost:11434\"   # Ollama API URL (default: localhost:11434)
```

## Ollama Setup

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model (choose one):
ollama pull llama3.1         # Best balance (recommended)
ollama pull qwen2.5:7b       # Best quality  
ollama pull llama3.2:1b      # Fastest

# Start Ollama (runs automatically on install)
ollama serve
```

## Entry Format

## Obsidian Integration\n\nThis system is designed to work seamlessly with Obsidian's powerful backlinking features:\n\n**📖 Automatic Backlinks**: Uses `[[YYYY-MM-DD]]` format that Obsidian recognizes natively\n**🔍 Backlinks Panel**: View cognitive connections in Obsidian's right sidebar\n**🕸️ Graph View**: See your intellectual network visually in Obsidian's graph\n**🔗 Linked/Unlinked Mentions**: Obsidian automatically shows where entries reference each other\n\n**Pro tip**: After completing an entry, open it in Obsidian and check the Backlinks panel to explore your cognitive network!\n\n## Entry Format\n\nFiles: `YYYY-MM-DD.md` in your diary directory"

```markdown
# Thursday, October 3, 2024

## 🤔 Reflection Prompts
**How did work play out today?**

## 💭 Brain Dump
Your thoughts...

---
**Related entries:** [[2024-09-28]], [[2024-09-30]]
```

## Claude Desktop Setup

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "obsidian-diary": {
      "command": "/Users/gps/.local/bin/uv",
      "args": ["run", "python", "src/obsidian_diary_mcp/server.py"],
      "cwd": "/Users/gps/Developer/obsidian-diary-mcp",
      "env": {
        "DIARY_PATH": "/Users/gps/Documents/diary"
      }
    }
  }
}
```

## Other MCP Clients

Works with other MCP-compatible tools. See [MCP documentation](https://modelcontextprotocol.io/) for setup.

**License**: MIT • **Requirements**: Python 3.8+, FastMCP
