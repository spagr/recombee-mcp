# recombee-mcp

A production-grade MCP (Model Context Protocol) server that wraps the [Recombee](https://www.recombee.com/) recommendation engine API, enabling AI agents to analyze, debug, and tune Recombee deployments through natural-language conversation.

## Status

🚧 **Under active development** — targeting v0.1.0 (read-only tools).

## Quick Start

```bash
git clone https://github.com/spagr/recombee-mcp.git
```

```bash
cd recombee-mcp
```

```bash
cp .env.example .env
```

Edit `.env` with your Recombee credentials, then:

```bash
uv sync
```

```bash
uv run recombee-mcp
```

Optionally, install as a global tool so `recombee-mcp` is available everywhere:

```bash
uv tool install .
```

### Claude Desktop Configuration

Add to your Claude Desktop `claude_desktop_config.json`.

**From a local clone** (recommended for development — always uses current code):

```json
{
  "mcpServers": {
    "recombee": {
      "command": "uv",
      "args": ["run", "--directory", "/absolute/path/to/recombee-mcp", "recombee-mcp"],
      "env": {
        "RECOMBEE_DB_ID": "your-database-id",
        "RECOMBEE_PRIVATE_TOKEN": "your-private-token",
        "RECOMBEE_REGION": "eu-west"
      }
    }
  }
}
```

Replace `/absolute/path/to/recombee-mcp` with the actual path to your clone.

**After `uv tool install .`** (cleaner, but requires reinstall after code changes):

```json
{
  "mcpServers": {
    "recombee": {
      "command": "recombee-mcp",
      "env": {
        "RECOMBEE_DB_ID": "your-database-id",
        "RECOMBEE_PRIVATE_TOKEN": "your-private-token",
        "RECOMBEE_REGION": "eu-west"
      }
    }
  }
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `describe_setup` | Server configuration and database schema overview |
| `recommend_to_user` | Personalized item recommendations for a user |
| `recommend_to_item` | Related items ("because you viewed") |
| `recommend_next_items` | Pagination for previous recommendations |
| `search_items` | Personalized full-text search |
| `get_item_properties` | All property values for one item |
| `list_items` | Paginated item listing with optional filter |
| `list_item_properties` | Item property schema |
| `list_user_properties` | User property schema |
| `get_user_properties` | All property values for one user |
| `list_segmentations` | Configured segmentations |
| `recommend_segments_to_user` | Top segments (categories/brands) for a user |

## Security

This server is **read-only by default**. No destructive operations (`Delete*`, `ResetDatabase`) are ever exposed. See [SECURITY.md](SECURITY.md) for the full security model.

## Development

```bash
uv sync --all-extras
```

```bash
uv run ruff check .
```

```bash
uv run mypy src/
```

```bash
uv run pytest
```

## License

[MIT](LICENSE)
