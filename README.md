# Obsidian Diary MCP Server

MCP server for AI-powered journaling with dynamic prompts and smart backlinking. Designed to be used alongside MCP-compatible CLI tools.

**Features**: Dynamic AI prompts • Hybrid memory links • Obsidian integration

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

## Daily Workflow

1. **Create entry**: `copilot "use create_diary_entry_file"` - Generates file with AI-powered reflection prompts
2. **Write in Obsidian** - Answer prompts and add your thoughts using the generated template
3. **Complete entry**: `copilot "use complete_diary_entry"` - Auto-generates temporal and topic backlinks

**Additional Commands:**
- `copilot "use list_recent_entries"` - View recent diary entries with dates
- `copilot "use read_diary_entry for 2024-10-03"` - Read specific entry by date
- `copilot "use update_entry_backlinks for 2024-10-03"` - Refresh backlinks for one entry
- `copilot "use refresh_all_backlinks"` - Update backlinks across all entries (performance optimized)

## Troubleshooting

**MCP Server Issues:**
- Check Copilot config exists: `cat ~/.copilot/mcp-config.json`
- Verify start script is executable: `chmod +x start-server.sh`
- Test server manually: `./start-server.sh` (should start without errors)
- Restart Copilot CLI after configuration changes

**Environment Issues:**
- Verify DIARY_PATH directory exists: `ls -la $DIARY_PATH`
- Check Python/uv installation: `uv --version`
- Confirm Ollama is running: `curl http://localhost:11434/api/tags`
- Test Ollama model: `ollama run llama3.1 "test"`

**Tool Execution:**
- Use explicit tool syntax: `copilot "use create_diary_entry_file tool"`
- Check available tools: `copilot "what MCP tools are available?"`
- Verify date format: Use YYYY-MM-DD format for date parameters

## How It Works

- **AI-Generated Prompts**: Ollama LLM analyzes your recent entries to create personalized reflection questions that avoid repetition
- **Hybrid Memory Links**: Automatically generates both `[[YYYY-MM-DD]]` temporal backlinks for chronological connections and `#topic-name` tags for thematic relationships
- **Performance Optimization**: Smart theme caching system reduces AI API calls by 90% by reusing cognitive analysis across related entries
- **Dynamic Content**: No hardcoded prompts or themes - everything adapts to your unique writing patterns and cognitive development over time
- **Obsidian Native**: Full integration with Obsidian's Backlinks panel, Tags panel, and Graph view for comprehensive knowledge discovery

## Available Tools

- `create_diary_entry_file(date?, focus?)` - Create new entry file with AI-generated reflection prompts. Optional date (defaults to today) and focus theme
- `complete_diary_entry(date?)` - Finalize entry by auto-generating both temporal backlinks and topic tags based on content analysis
- `read_diary_entry(date)` - Read existing diary entry by date (YYYY-MM-DD format)
- `list_recent_entries(count?)` - Display recent diary entries with dates. Optional count parameter (defaults to 5)
- `update_entry_backlinks(date)` - Refresh temporal and topic backlinks for specific entry using cached theme analysis
- `refresh_all_backlinks()` - Batch update backlinks across all entries with performance optimization via caching
- `save_diary_entry(date, content)` - Save diary entry with automatic backlink generation

## Configuration

```bash
export DIARY_PATH="/path/to/diary"           # Required
export OLLAMA_MODEL="llama3.1:latest"        # Optional
```

## Ollama Setup

```bash
# Install and pull model
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1
```

## Obsidian Integration

- **Temporal Backlinks**: Uses `[[YYYY-MM-DD]]` format for chronological connections that Obsidian recognizes natively
- **Topic Tags**: Generates `#theme-name` hashtags from AI analysis for thematic categorization and filtering
- **Backlinks Panel**: View temporal connections and referenced entries in Obsidian's right sidebar
- **Tags Panel**: Browse entries by cognitive themes and emotional patterns using the tag browser
- **Graph View**: Visualize your intellectual and emotional network with both temporal and thematic connections
- **Search Integration**: Find entries through Obsidian's powerful search using dates, tags, or content matching
- **Linked Mentions**: Automatic detection of unlinked references between entries for comprehensive connectivity

## Entry Format

Files are stored as `YYYY-MM-DD.md` in your diary directory:

```markdown
# Thursday, October 3, 2024

## Reflection Prompts
**How did work play out today?**
**What patterns am I noticing in my thinking?**
**What challenged me most today and why?**

## Brain Dump
Your thoughts and experiences...

---
## Memory Links
**Temporal:** [[2024-09-28]] • [[2024-09-30]]
**Topics:** #work-stress #personal-growth #decision-making
```

## GitHub Copilot CLI Setup

1. **Install**: `npm install -g @github/copilot`
2. **Launch**: `copilot`
3. **Add MCP server**: `/mcp add`
   - **Name**: `diary`
   - **Command**: `/Users/gps/Developer/obsidian-diary-mcp/start-server.sh`
   - **Environment**: `DIARY_PATH=/Users/gps/Documents/diary`
4. **Save**: Ctrl+S

**Config example** (`~/.copilot/mcp-config.json`):
```json
{
  "mcpServers": {
    "diary": {
      "command": "/Users/gps/Developer/obsidian-diary-mcp/start-server.sh",
      "env": {
        "DIARY_PATH": "/Users/gps/Documents/diary"
      }
    }
  }
}
```

**License**: MIT • **Requirements**: Python 3.8+, FastMCP
