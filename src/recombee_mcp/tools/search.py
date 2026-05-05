"""Search tools — personalized full-text search."""

from typing import Any

from recombee_api_client.api_requests import SearchItems
from recombee_api_client.exceptions import APIException

from recombee_mcp.errors import ToolError


def register_search_tools(mcp: Any, ctx: Any) -> None:
    """Register search tools with the MCP server."""

    @mcp.tool()
    def search_items(
        user_id: str,
        search_query: str,
        count: int = 10,
        scenario: str | None = None,
        filter: str | None = None,  # noqa: A002
        booster: str | None = None,
        return_properties: bool = True,
    ) -> dict[str, Any]:
        """Perform personalized full-text search across items.

        Combines text matching with the user's preference model for personalized results.

        Args:
            user_id: The user performing the search (for personalization).
            search_query: The text query to search for.
            count: Number of results to return (1-100).
            scenario: Scenario name for context-specific search.
            filter: ReQL filter expression to narrow results.
            booster: ReQL booster expression to influence ranking.
            return_properties: Whether to include item properties in results.
        """
        count = min(max(count, 1), 100)
        params: dict[str, Any] = {
            "user_id": user_id,
            "search_query": search_query,
            "count": count,
        }
        if scenario:
            params["scenario"] = scenario

        ctx.audit.log(
            profile=ctx.settings.profile,
            db_id=ctx.settings.db_id,
            tool_name="search_items",
            parameters=params,
            outcome="success",
        )
        try:
            request = SearchItems(
                user_id,
                search_query,
                count,
                scenario=scenario,
                filter=filter or None,
                booster=booster or None,
                return_properties=return_properties,
            )
            result = ctx.client.send(request)
        except APIException as e:
            raise ToolError("search_items", str(e)) from e
        return {
            "database_id": ctx.settings.db_id,
            "user_id": user_id,
            "search_query": search_query,
            "recomm_id": result.get("recommId"),
            "recomms": result.get("recomms", []),
        }
