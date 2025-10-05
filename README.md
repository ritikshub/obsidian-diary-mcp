# Obsidian Diary MCP Server

Journaling unlocks mental clarity and space for growth. This system combines Obsidian with local AI to help you reflect deeply.

**Privacy note:** Your diary content and AI analysis stay on your machine via Ollama. The AI CLI acts as an interface to create and link entries. To read your entries, open them directly in Obsidian or your text editor—don't use the CLI to avoid sending content to external APIs.

## What You Need

- uv
- Ollama
- GitHub Copilot CLI or any AI cli
- Dedicated Obsidian vault for entries

## Quick Startf

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
- Environment: `DIARY_PATH=/path/to/your/diary-vault`

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

**Optional: Auto-approve diary tools Copilot example** 

Add to `~/.config/copilot/config.json` (or `$XDG_CONFIG_HOME/copilot/config.json`):
```json
{
  "allowedTools": ["diary"]
}
```

Or pass it each time you start:
```bash
copilot --allow-tool "diary"
```

**1. Start your session:**
```bash
copilot
```

**2. Create today's memory log:**
```
"create a memory log for today"
```
→ Generates a file with AI-powered reflection prompts based on your recent entries

**3. Open in Obsidian and write:** (or in terminal, it is just a .md file)
- Reflect on the prompts
- Free-write in the Brain Dump section

**4. Link when done:**
```
"link today's memory log"
```
→ Auto-generates temporal connections `[[YYYY-MM-DD]]` and topic tags `#theme`

**5. Explore connections:**
- Use Obsidian's backlinks panel to see related entries
- View graph to visualize your thinking patterns over time

**Privacy-safe insights:**
- `"show me themes from the last week"` - See recurring topics without exposing content
- `"what themes have I been thinking about lately"` - Get theme analysis

**6. Generate a Memory Trace (periodic review):**
```
"create a memory trace for the last 30 days"
"generate a memory trace for the last 3 months"
"create a memory trace analyzing the last year"
```
→ Creates a comprehensive analysis document with:
  - Timeline visualization of your journey
  - Core theme evolution across time periods
  - Pattern recognition and recurring cycles
  - Relationship maps and growth trajectories
  - Wisdom extracted from your entries
  - Significant moments timeline

The trace is saved as `memory-trace-YYYY-MM-DD.md` in your diary vault for easy reference in Obsidian.

**To read your entries:**
- Open them directly in Obsidian (recommended for backlinks/graph)
- Or view in any text editor—they're just markdown files in `DIARY_PATH`
- Avoid using CLI read commands to keep content private

## If It Breaks

- Check config: `cat ~/.copilot/mcp-config.json` or wherever your cli logs go
- Make script runnable: `chmod +x start-server.sh`
- Test it: `./start-server.sh`
- Check server logs: `tail -f logs/server-$(date +%Y-%m-%d).log`
- View all logs: `ls -lh logs/`
- Restart your CLI


## How It Works

- **Local AI**: Ollama processes your entries locally—your journal content never leaves your machine
- **AI CLI Interface**: Your CLI (Copilot, Claude Desktop, etc.) provides the interface via MCP protocol
- **Smart Prompts**: Analyzes recent entries to generate contextual reflection questions
- **Auto-linking**: Creates temporal `[[YYYY-MM-DD]]` and topic `#tag` connections  
- **Caching**: Stores theme analysis in-memory to avoid redundant AI calls
- **Sunday Special**: 5 prompts synthesizing the past 7 calendar days (vs. 3 prompts from recent entries normally)


## Memory Log Format

Files are stored as `YYYY-MM-DD.md` in your diary vault:

**Regular Day (3 prompts):**
```markdown
## 🧠 Reflection Prompts

*Building on insights from previous entries*

**1. What cognitive patterns or mental models shaped your thinking this period?**

**2. How do your current challenges reflect deeper philosophical questions about identity and meaning?**

**3. What assumptions about reality, success, or relationships are being tested right now?**

---

## 💭 Brain Dump

*Your thoughts, experiences, and observations...*


---

## 🔗 Memory Links

*Temporal connections and topic tags will be auto-generated when you complete the entry.*
```

**Sunday (5 prompts + weekly synthesis):**
```markdown
## 🌅 Weekly Synthesis & Alignment

*A deeper reflection on the past week and intentional focus for the week ahead*

**1. What patterns from this past week reveal deeper truths about your cognitive frameworks?**

**2. How did your decision-making processes evolve throughout the week?**

**3. What assumptions about progress and growth were challenged this week?**

**4. Where do you need to realign your mental models for the upcoming week?**

**5. What philosophical questions emerged from this week's experiences that deserve deeper exploration?**

---

## 💭 Brain Dump

*Your thoughts, experiences, and observations...*


---

## 🔗 Memory Links

*Temporal connections and topic tags will be auto-generated when you complete the entry.*
```

**After completion, memory links are added:**
```markdown
## 🔗 Memory Links

**Temporal:** [[2024-09-28]] • [[2024-09-30]] • [[2024-10-01]]
**Topics:** #work-stress #personal-growth #decision-making #cognitive-patterns
```

**License**: MIT • **Requirements**: Python 3.13+, FastMCP 2.12.4+, Ollama