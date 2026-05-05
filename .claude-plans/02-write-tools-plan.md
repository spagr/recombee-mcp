# 02 — Write Tools (M2)

## Goal

Add write tools to the MCP server for item property updates, scenario filter
modifications, and test-data generation in sandbox environments.

## Context

M1 delivers read-only tools. M2 adds controlled write access for sandbox
databases only, following the security model in CLAUDE.md §4.2.

## Approach

TBD — to be detailed when M2 work begins.

Key principles:
- Write tools only registered when `profile=sandbox` AND `write_enabled=true`
- Every write tool has `confirm: bool = False` (dry-run by default)
- Security auditor agent runs before merge
- No `Delete*` or `Reset*` operations ever

## Status

Draft
