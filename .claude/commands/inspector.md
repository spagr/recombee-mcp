# /inspector

Launch the MCP Inspector for interactive tool testing.

## Usage

`/inspector`

## What it does

Run the FastMCP development inspector UI:

```bash
uv run fastmcp dev src/recombee_mcp/server.py
```

This opens a web UI where you can:
- See all registered tools
- Test tool calls interactively
- Inspect JSON schemas
- View request/response pairs

Note: Requires valid RECOMBEE_DB_ID and RECOMBEE_PRIVATE_TOKEN in .env.
