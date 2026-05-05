# /new-tool

Scaffold a new MCP tool for the Recombee MCP server.

## Usage

`/new-tool <tool_name>`

## What it does

1. Determine which module the tool belongs to (recommendations, catalog, search, segments, or meta)
2. Add the tool function stub to the appropriate module in `src/recombee_mcp/tools/`
3. Create a test file stub in `tests/unit/tools/` (or add to existing)
4. The tool function should:
   - Have a complete docstring with Args section
   - Include audit logging
   - Catch `APIException` and raise `ToolError`
   - Return a dict with `database_id` in metadata
   - Cap count parameters appropriately

## Template

```python
@mcp.tool()
def tool_name(
    required_param: str,
    optional_param: int = 10,
) -> dict[str, Any]:
    """One-line description.

    Detailed description for the LLM.

    Args:
        required_param: What this is.
        optional_param: What this controls.
    """
    ctx.audit.log(
        profile=ctx.settings.profile,
        db_id=ctx.settings.db_id,
        tool_name="tool_name",
        parameters={"required_param": required_param},
        outcome="success",
    )
    try:
        result = ctx.client.send(SomeRequest(...))
    except APIException as e:
        raise ToolError("tool_name", str(e)) from e
    return {"database_id": ctx.settings.db_id, ...}
```
