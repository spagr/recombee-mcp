# 01 — Initial Implementation (M1: Read-Only Tools)

## Goal

Build the complete read-only MCP server wrapping Recombee API. Ship all 12 tools
from the M1 spec with tests, CI, and documentation.

## Context

Brand-new project. Primary user is an e-commerce consultant operating Recombee
for a Czech premium kitchenware e-shop. The server will be used via Claude Desktop
and Claude Code for debugging and tuning recommendations.

## Approach

7 phases executed sequentially:

1. **Repo skeleton** — pyproject.toml, .gitignore, LICENSE, README, directory structure
2. **Foundation modules** — settings, errors, audit logger with tests
3. **Client + first tool** — RecombeeClient factory, FastMCP server, describe_setup tool
4. **Read-only tools** — all 11 remaining tools, one module at a time, each with tests
5. **Pre-commit + CI** — hooks, GitHub Actions workflows
6. **Claude Code config** — .claude/ directory, skills, commands, agents, .mcp.json
7. **Polish** — docs, final README, lean CLAUDE.md, M2 draft plan

## Test Plan

- Unit tests mock the Recombee SDK — never hit real API
- Each tool has happy-path + error-path tests
- Coverage target: 90% for tools/, 60% for plumbing
- Integration tests in tests/integration/ (skipped without credentials)

## Risks

- FastMCP API changes — mitigated by checking current docs
- Recombee SDK sync nature — FastMCP supports sync handlers natively
- Cross-platform paths — use pathlib + platformdirs everywhere

## Rollback

Each phase is a separate commit. Revert individual commits if needed.

## Status

In progress

## Notes

- 2026-05-05: Plan approved, starting Phase 1
