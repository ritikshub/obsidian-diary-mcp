# Obsidian Diary MCP Server

AI-powered journaling with local processing, automatic backlinks, and smart prompts. Combines Obsidian with Ollama for deep reflection.

**Privacy:** All AI processing is local via Ollama. Content never leaves your machine.

## Features

- 🧠 AI-generated reflection prompts based on recent entries
- 🔗 Automatic `[[YYYY-MM-DD]]` backlinks using theme similarity
- 🏷️ Smart `#tag` extraction from your writing
- ✅ Todo extraction to organized checklists
- 📊 Memory trace analysis with theme evolution
- 🗓️ Sunday synthesis (weekly reflection prompts)

## Requirements

- uv, Ollama (llama3.1 or compatible model), MCP client, Obsidian vault

## Setup

```bash
git clone https://github.com/madebygps/obsidian-diary-mcp.git
cd obsidian-diary-mcp
uv sync
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
- Environment: `DIARY_PATH=/path/to/your/diary-vault`

**Optional - Customize via `.env`:**

All settings have sensible defaults. Only create `.env` if you want to customize:

```bash
tail -f logs/debug-$(date +%Y-%m-%d).log  # Watch in real-time
grep ERROR logs/debug-*.log                # Find errors
grep "similarity" logs/debug-*.log         # Debug backlinks
```

## Troubleshooting

**Server issues:** Check `.env` exists with `DIARY_PATH` and `PLANNER_PATH` set. Run `./start-server.sh` directly to test.

**Ollama issues:** Verify running with `curl http://localhost:11434/api/tags`. Pull model: `ollama pull llama3.1:latest`

**No backlinks:** Need 2+ entries with similar themes (>8% overlap). Check Brain Dump has content: `grep "similarity" logs/debug-*.log`

**Timeouts:** Increase `OLLAMA_TIMEOUT` (90+) and `OLLAMA_NUM_PREDICT` (2000+) for reasoning models.


## How It Works

- **Local AI**: Ollama processes entries locally—content never leaves your machine
- **Brain Dump Focus**: Analyzes your writing (not prompts) for themes
- **Smart Prompts**: Context-aware questions based on recent entries
- **Auto-linking**: Jaccard similarity connects entries with >8% theme overlap
- **Sundays**: 5 weekly synthesis prompts (vs 3 daily)
- **Todo Extraction**: AI identifies action items and creates checklists


## Entry Format

Each entry (`YYYY-MM-DD.md`):
1. **Reflection Prompts** (3-5 AI-generated questions)
2. **Brain Dump** (your freeform writing)
3. **Memory Links** (auto-generated: `[[YYYY-MM-DD]]` backlinks + `#tags`)

## License

MIT • Python 3.13+ • FastMCP 2.12.4+ • Ollama