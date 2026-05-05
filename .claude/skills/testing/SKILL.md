# Testing Conventions

## Structure

- `tests/unit/` — mocked tests, no real API calls
- `tests/integration/` — real sandbox, skipped without credentials
- `tests/conftest.py` — shared fixtures

## Fixtures (from conftest.py)

- `settings` — Settings with test values (sandbox profile)
- `mock_client` — MagicMock for RecombeeClient
- `audit_logger` — AuditLogger writing to tmp_path
- `ctx` — ServerContext with all above combined
- `mcp` — Fresh FastMCP("test") instance

## How to Access Registered Tools

```python
from tests.conftest import get_tool

# After registering tools:
register_xxx_tools(mcp, ctx)
tool = get_tool(mcp, "tool_name")
result = tool.fn(arg1="value")
```

## Mocking the SDK

```python
ctx.client.send = MagicMock(return_value={"recommId": "r1", "recomms": [...]})
# or for errors:
ctx.client.send = MagicMock(side_effect=APIException(404, "Not found"))
```

## Test Naming

`test_<unit>_<scenario>_<expectation>`

Example: `test_recommend_to_user_with_invalid_scenario_raises_value_error`

## Coverage

- Target 90% for `tools/`
- Target 60% for plumbing modules
- Each tool needs happy-path + error-path test minimum
