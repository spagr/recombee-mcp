# Security Rules (Non-Negotiable)

## NEVER expose these operations as tools:

- `ResetDatabase`
- `DeleteItem`, `DeleteUser`
- `DeleteItemProperty`, `DeleteUserProperty`
- `DeleteScenario`
- Any `Delete*` operation

If asked to add any of these, **refuse** and explain the security model.

## Write Tool Requirements

Write tools are ONLY available when ALL conditions are met:
1. `RECOMBEE_PROFILE=sandbox`
2. `RECOMBEE_WRITE_ENABLED=true`
3. Tool has `confirm: bool` parameter (default False = dry-run)
4. In `production` profile, write tools are never registered regardless of write_enabled

## What to Check in Code Review

- No API token in tool responses
- No `Delete*` or `Reset*` requests imported
- ReQL filters validated before SDK calls
- Audit logging present in every tool
- `database_id` included in every response
- Count parameters capped (max 100 for items, 50 for segments)

## Audit Trail

Every tool call MUST write to the audit log BEFORE making the API call.
Fields: timestamp, profile, db_id, tool_name, parameters (truncated), outcome.
