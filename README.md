# Obsidian Diary MCP Server

Journaling unlocks mental clarity and space for growth. This system combines Obsidian with local AI to help you reflect deeply.

**Privacy note:** Your diary content is processed locally by Ollama and never leaves your machine. GitHub Copilot CLI (or other MCP clients) acts as an interface to invoke tools, but [does not retain prompts or responses for training](https://resources.github.com/learn/pathways/copilot/essentials/how-github-copilot-handles-data/) when using MCP tools. To read your entries, open them directly in Obsidian or your text editor.

## What You Need

- uv
- Ollama
- GitHub Copilot CLI or any AI cli
- Dedicated Obsidian vault for entries

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

**7. Add MCP server to your AI CLI:**

I use GitHub Copilot CLI, but any MCP-capable CLI works.


**Required:**
- Name: `diary`
- Command: `/full/path/to/obsidian-diary-mcp/start-server.sh`
- Environment: '$env:DIARY_PATH = "C:\Users\Ritik Roushan\Documents\Obsidian Vault"'

**Optional - Customize via `.env`:**

All settings have sensible defaults. Only create `.env` if you want to customize:

```bash
cp .env.example .env
# Edit to override defaults
```

**Available settings (all optional):**

| Setting | Default | Description |
|---------|---------|-------------|
| `DIARY_PATH` | `~/Documents/diary` | Path to your diary vault |
| `RECENT_ENTRIES_COUNT` | `3` | Number of recent entries to analyze for regular days (Sundays use past 7 calendar days) |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama API endpoint |
| `OLLAMA_MODEL` | `llama3.1:latest` | LLM model to use |
| `OLLAMA_TIMEOUT` | `30` | Request timeout in seconds |
| `OLLAMA_TEMPERATURE` | `0.7` | Creativity level (0.0-1.0) |
| `OLLAMA_NUM_PREDICT` | `200` | Max tokens to generate |


## Daily Workflow

**Optional:** Auto-approve tools by adding `{"allowedTools": ["diary"]}` to `~/.config/copilot/config.json`

1. **Create:** `"create a memory log for today"` → Generates file with AI prompts
2. **Write:** Open in Obsidian, reflect on prompts, free-write in Brain Dump section
3. **Link:** `"link today's memory log"` → Auto-generates `[[YYYY-MM-DD]]` connections and `#tags`
4. **Explore:** Use Obsidian's backlinks panel and graph view

**Insights:** `"show me themes from the last week"`

**Memory Trace:** `"create a memory trace for the last 30 days"` → Comprehensive analysis with timeline, theme evolution, patterns, and wisdom (saved as `memory-trace-YYYY-MM-DD.md`)

## If It Breaks

- Check config: `cat ~/.copilot/mcp-config.json` or wherever your cli logs go
- Make script runnable: `chmod +x start-server.sh`
- Test it: `./start-server.sh`
- Check server logs: `tail -f logs/server-$(date +%Y-%m-%d).log`
- View all logs: `ls -lh logs/`
- Restart your CLI


## How It Works

- **Local AI**: Ollama processes entries locally—content never leaves your machine
- **Brain Dump Focus**: Analyzes your actual writing (not the prompts) for themes and connections
- **Smart Prompts**: Identifies areas needing deeper reflection across different life themes
- **Auto-linking**: Connects entries with similar Brain Dump content via `[[YYYY-MM-DD]]` and `#tags`
- **Sundays**: 5 prompts synthesizing entries from the past 7 calendar days (vs 3 from recent entries normally)


## Entry Format

Each entry (`YYYY-MM-DD.md`) contains:

1. **Reflection Prompts** (3 for weekdays, 5 for Sundays) - AI-generated questions based on your recent Brain Dump content
2. **Brain Dump** - Your freeform writing, reflections, and experiences
3. **Memory Links** - Auto-generated after completion:
   - Temporal connections: `[[2024-09-28]]` `[[2024-09-30]]`
   - Topic tags: `#work-life-balance` `#personal-growth`

**License**: MIT • **Requirements**: Python 3.13+, FastMCP 2.12.4+, Ollama