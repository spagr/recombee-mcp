# Recombee API Conventions

## SDK Usage

- Import requests from `recombee_api_client.api_requests`
- Import exceptions from `recombee_api_client.exceptions` — class is `APIException`
- Client method is `client.send(request)` — synchronous
- All requests are classes: `RecommendItemsToUser(user_id, count, **kwargs)`

## Common Request Patterns

```python
from recombee_api_client.api_requests import RecommendItemsToUser

request = RecommendItemsToUser(
    user_id,
    count,
    scenario=scenario,
    filter=filter_expr or None,
    booster=booster_expr or None,
    return_properties=True,
)
result = client.send(request)
# result is a dict with "recommId" and "recomms" keys
```

## Error Handling

- Catch `APIException` — base class for all API errors
- `ResponseException` — HTTP error response from API
- `ApiTimeoutException` — request timed out
- Always wrap in `ToolError` for MCP response

## Region Mapping

- `eu-west` → `client-rapi-eu-west.recombee.com`
- `us-west` → `client-rapi-us-west.recombee.com`
- `ap-se` → `client-rapi-ap-se.recombee.com`
- `ca-east` → `client-rapi-ca-east.recombee.com`
