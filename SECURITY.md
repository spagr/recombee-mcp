# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | ✅ Current          |

## Security Model

This MCP server handles a Recombee private API token that has full database access. The following safeguards are enforced:

1. **No destructive operations** — `ResetDatabase`, `Delete*` operations are never exposed as tools.
2. **Read-only by default** — Write tools require `RECOMBEE_WRITE_ENABLED=true` AND `RECOMBEE_PROFILE=sandbox`.
3. **Audit logging** — Every tool call is logged to a local JSONL file.
4. **Write confirmation** — Write tools require explicit `confirm=True` parameter (dry-run by default).
5. **ReQL validation** — User-supplied filter strings are validated against an allowlist.
6. **No secrets in responses** — API tokens are never included in tool outputs.

## Reporting a Vulnerability

If you discover a security vulnerability, please report it via [GitHub Security Advisories](https://github.com/spagr/recombee-mcp/security/advisories/new).

Do **not** open a public issue for security vulnerabilities.

We will acknowledge receipt within 48 hours and provide a fix timeline within 7 days.
