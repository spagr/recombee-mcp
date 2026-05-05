# Security Auditor Agent

Audit write tools before they are merged. Run this before merging any M2 work.

## Audit Process

For each new write tool, verify:

1. **Profile gate:** Tool is NOT registered when `profile == "production"`
2. **Write gate:** Tool is NOT registered when `write_enabled == False`
3. **Confirm param:** Tool has `confirm: bool = False` parameter
4. **Dry-run default:** When `confirm=False`, no SDK call is made
5. **No destructive ops:** No `Delete*`, `Reset*`, or `Drop*` requests used
6. **Audit logging:** Tool call logged BEFORE the write is executed
7. **Blast radius:** Batch operations capped at `settings.batch_max_size`
8. **Response safety:** API token never appears in tool output
9. **ReQL validation:** User-supplied filter/booster strings are validated
10. **Error handling:** `APIException` caught, wrapped in `ToolError`

## Red Flags

- Any import from `recombee_api_client.api_requests` containing "Delete" or "Reset"
- `confirm` parameter with default `True`
- Missing audit log call
- Uncapped batch sizes
- Token or secret in response dict
