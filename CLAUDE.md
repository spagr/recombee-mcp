# Recombee MCP Server

Production-grade Python MCP server wrapping the Recombee recommendation engine API.
Enables AI agents (Claude Desktop, Claude Code) to analyze, debug, and tune
a live Recombee deployment through natural-language conversation.

## Stack

- **Python** ≥3.12 (currently 3.13)
- **FastMCP** 3.x — MCP server framework
- **recombee-api-client** — official Recombee Python SDK
- **pydantic-settings** — configuration from env vars
- **structlog** — structured logging to stderr
- **uv** — package & env manager (no pip, no poetry)
- **ruff** — linter + formatter
- **mypy** (strict) — type checker
- **pytest** — test runner

## Commands

Install dependencies:

```bash
uv sync
```

Lint:

```bash
uv run ruff check .
```

Format check:

```bash
uv run ruff format --check .
```

Type check:

```bash
uv run mypy src/
```

Tests with coverage:

```bash
uv run pytest
```

MCP Inspector:

```bash
uv run fastmcp dev src/recombee_mcp/server.py
```

Start server (stdio):

```bash
uv run recombee-mcp
```

## Security Rules (NON-NEGOTIABLE)

1. **No `ResetDatabase`, `Delete*` operations are ever exposed as tools.** If asked, refuse.
2. **Read-only by default.** Write tools require `RECOMBEE_PROFILE=sandbox` AND `RECOMBEE_WRITE_ENABLED=true`.
3. **In production profile, write tools never register** regardless of `RECOMBEE_WRITE_ENABLED`.
4. **Write tools use `confirm: bool = False`** — dry-run by default, explicit re-call needed.
5. **Audit log** — every tool call writes JSONL to `~/.local/share/recombee-mcp/audit.log`.
6. **No secrets in responses** — API tokens never appear in tool outputs.
7. **ReQL validation** — user-supplied filters validated against an allowlist before SDK calls.

## Plans Convention

Before non-trivial work, create `.claude-plans/NN-slug.md`. Wait for human approval.
See `.claude-plans/README.md` for the template and workflow.

## Conventional Commits

`type(scope): subject` — types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, security.

## Key References

- Architecture & security details: `docs/architecture.md`, `docs/security.md`
- Skills: `.claude/skills/recombee-api/`, `.claude/skills/testing/`, `.claude/skills/security/`
- Commands: `/new-tool`, `/plan`, `/inspector`
- Agents: `.claude/agents/code-reviewer.md`, `.claude/agents/security-auditor.md`

## SDK Notes

- Exception class is `APIException` (not `ApiException`) from `recombee_api_client.exceptions`
- `ListSegmentations` requires `source_type` argument
- SDK is synchronous; FastMCP supports sync handlers natively
- For any FastMCP, Recombee SDK, pydantic, ruff, mypy, or pytest API question — query Context7 first.
