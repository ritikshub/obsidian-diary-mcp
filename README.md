# Obsidian Diary MCP Server

Establish a daily journaling habit that'll unlock superpowers in your career and life. AI analyzes your entries to generate personalized prompts while keeping everything local.

**What it enables**: Daily reflection • Smart prompts • Complete privacy

## What You Need

**Software:**
- uv (Python installer)
- Ollama (runs AI locally, ~5GB)
- A CLI that works with MCP

**For Obsidian:**
- A dedicated Obsidian vault that only contains diary entries
- Read/write access to that vault

## Quick Start

**1. Clone the repo:**
```bash
git clone https://github.com/madebygps/obsidian-diary-mcp.git
```

**2. Enter directory:**
```bash
cd obsidian-diary-mcp
```

**3. Install dependencies:**
```bash
uv sync
```

**4. Make script executable:**
```bash
chmod +x start-server.sh
```

**5. Install GitHub Copilot CLI:**
```bash
npm install -g @github/copilot
```

**6. Launch Copilot:**
```bash
copilot
```

**7. Add MCP server:**
```bash
/mcp add
```
Provide these values: 

- Name: `diary`, 
- Command: `/full/path/to/obsidian-diary-mcp/start-server.sh`, 
- Environment: `DIARY_PATH=/path/to/your/diary-vault`

## How to Use

**Best way: Use Copilot CLI interactively**

1. Start Copilot CLI: `copilot`
2. In the interactive session, use natural prompts:
   - "create a diary entry for today"
   - "show me my recent entries"
   - "complete today's entry with backlinks"
   - "read my entry from October 3rd"

**Alternative: Command line usage**
- `copilot "use create_diary_entry_file"` - Make new entry
- `copilot "use list_recent_entries"` - See recent entries
- `copilot "use complete_diary_entry"` - Add backlinks when done
- `copilot "use read_diary_entry for 2024-10-03"` - Read specific entry

## If It Breaks


**Server problems:**
- Check config: `cat ~/.copilot/mcp-config.json`
- Make script runnable: `chmod +x start-server.sh`
- Test it: `./start-server.sh`
- Restart your CLI

**Other problems:**
- Check diary folder exists: `ls -la $DIARY_PATH`
- Check uv works: `uv --version`
- Check Ollama runs: `curl http://localhost:11434/api/tags`
- Test AI: `ollama run llama3.1 "test"`

**Command problems:**
- Be specific: `copilot "use create_diary_entry_file tool"`
- Check what's available: `copilot "what MCP tools are available?"`
- Use YYYY-MM-DD for dates


## How It Works

- **Prompts**: Reads your old entries and makes new questions
- **Links**: Connects entries by date `[[2024-10-03]]` and topic `#work-stress`
- **Fast**: Caches stuff so it doesn't ask AI the same thing twice
- **Adaptive**: No hardcoded content, learns from your writing
- **Obsidian**: Works with backlinks, tags, and graph view


## Entry Format

Files are stored as `YYYY-MM-DD.md` in your diary vault:

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

**License**: MIT • **Requirements**: Python 3.8+, FastMCP