# Claude Desktop Configuration

To use this MCP server with Claude Desktop, add the following to your Claude Desktop configuration file.

## Configuration File Location

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

## Configuration

Add this to your `mcpServers` section:

```json
{
  "mcpServers": {
    "obsidian-diary": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/gps/Documents/diary/obsidian-diary-mcp",
        "run",
        "obsidian-diary-mcp"
      ]
    }
  }
}
```

## Full Example

If your config file is empty or you want to see a complete example:

```json
{
  "mcpServers": {
    "obsidian-diary": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/gps/Documents/diary/obsidian-diary-mcp",
        "run",
        "obsidian-diary-mcp"
      ]
    }
  }
}
```

## After Configuration

1. Save the configuration file
2. Restart Claude Desktop
3. The MCP server should now be available
4. You can verify it's working by asking Claude to use the diary tools

## Example Prompts to Try

Once configured, try these prompts with Claude:

- "Create a diary template for today"
- "List my recent diary entries"
- "Read my entry from 2025-10-03"
- "Save this diary entry for today: [your content]"
- "Update the backlinks for my entry from 2025-10-03"

## Troubleshooting

If the server doesn't connect:

1. Verify `uv` is in your PATH: `which uv`
2. Test the server manually: `cd /Users/gps/Documents/diary/obsidian-diary-mcp && uv run obsidian-diary-mcp`
3. Check Claude Desktop logs for error messages
4. Ensure the path in the config matches your actual directory structure

## Using the MCP Inspector for Development

To test and debug the server interactively:

```bash
cd /Users/gps/Documents/diary/obsidian-diary-mcp
uv run fastmcp dev src/obsidian_diary_mcp/server.py
```

This opens a web interface where you can test all tools without needing Claude Desktop.
