"""Recommendation tools — personalized and item-to-item recommendations."""

from typing import Any

from recombee_api_client.api_requests import (
    RecommendItemsToItem,
    RecommendItemsToUser,
    RecommendNextItems,
)
from recombee_api_client.exceptions import APIException

from recombee_mcp.errors import ToolError


def register_recommendation_tools(mcp: Any, ctx: Any) -> None:
    """Register recommendation tools with the MCP server."""

    @mcp.tool()
    def recommend_to_user(
        user_id: str,
        count: int = 10,
        scenario: str | None = None,
        filter: str | None = None,  # noqa: A002
        booster: str | None = None,
        return_properties: bool = True,
    ) -> dict[str, Any]:
        """Get personalized item recommendations for a user.

        Args:
            user_id: The user to get recommendations for.
            count: Number of items to recommend (1-100).
            scenario: Scenario name for context-specific recommendations.
            filter: ReQL filter expression to narrow results.
            booster: ReQL booster expression to influence ranking.
            return_properties: Whether to include item properties in results.
        """
        count = min(max(count, 1), 100)
        params: dict[str, Any] = {"user_id": user_id, "count": count}
        if scenario:
            params["scenario"] = scenario
        if filter:
            params["filter"] = filter
        if booster:
            params["booster"] = booster

        ctx.audit.log(
            profile=ctx.settings.profile,
            db_id=ctx.settings.db_id,
            tool_name="recommend_to_user",
            parameters=params,
            outcome="success",
        )
        try:
            request = RecommendItemsToUser(
                user_id,
                count,
                scenario=scenario,
                filter=filter or None,
                booster=booster or None,
                return_properties=return_properties,
            )
            result = ctx.client.send(request)
        except APIException as e:
            raise ToolError("recommend_to_user", str(e)) from e
        return {
            "database_id": ctx.settings.db_id,
            "user_id": user_id,
            "scenario": scenario,
            "recomm_id": result.get("recommId"),
            "recomms": result.get("recomms", []),
        }

    @mcp.tool()
    def recommend_to_item(
        item_id: str,
        target_user_id: str | None = None,
        count: int = 10,
        scenario: str | None = None,
        filter: str | None = None,  # noqa: A002
        booster: str | None = None,
        return_properties: bool = True,
    ) -> dict[str, Any]:
        """Get related item recommendations ("because you viewed" / similar items).

        Args:
            item_id: The reference item to find related items for.
            target_user_id: Optional user for personalization of results.
            count: Number of items to recommend (1-100).
            scenario: Scenario name for context-specific recommendations.
            filter: ReQL filter expression to narrow results.
            booster: ReQL booster expression to influence ranking.
            return_properties: Whether to include item properties in results.
        """
        count = min(max(count, 1), 100)
        params: dict[str, Any] = {"item_id": item_id, "count": count}
        if target_user_id:
            params["target_user_id"] = target_user_id
        if scenario:
            params["scenario"] = scenario

        ctx.audit.log(
            profile=ctx.settings.profile,
            db_id=ctx.settings.db_id,
            tool_name="recommend_to_item",
            parameters=params,
            outcome="success",
        )
        try:
            request = RecommendItemsToItem(
                item_id,
                target_user_id or user_id_placeholder(),
                count,
                scenario=scenario,
                filter=filter or None,
                booster=booster or None,
                return_properties=return_properties,
            )
            result = ctx.client.send(request)
        except APIException as e:
            raise ToolError("recommend_to_item", str(e)) from e
        return {
            "database_id": ctx.settings.db_id,
            "item_id": item_id,
            "scenario": scenario,
            "recomm_id": result.get("recommId"),
            "recomms": result.get("recomms", []),
        }

    @mcp.tool()
    def recommend_next_items(
        recomm_id: str,
        count: int = 10,
    ) -> dict[str, Any]:
        """Get the next page of a previous recommendation request.

        Use this to paginate through recommendation results. Requires the recomm_id
        from a previous recommend_to_user or recommend_to_item call.

        Args:
            recomm_id: The recommendation ID from a previous request.
            count: Number of additional items to return.
        """
        count = min(max(count, 1), 100)
        ctx.audit.log(
            profile=ctx.settings.profile,
            db_id=ctx.settings.db_id,
            tool_name="recommend_next_items",
            parameters={"recomm_id": recomm_id, "count": count},
            outcome="success",
        )
        try:
            result = ctx.client.send(RecommendNextItems(recomm_id, count))
        except APIException as e:
            raise ToolError("recommend_next_items", str(e)) from e
        return {
            "database_id": ctx.settings.db_id,
            "recomm_id": result.get("recommId"),
            "recomms": result.get("recomms", []),
        }


def user_id_placeholder() -> str:
    """Placeholder user ID for item-to-item recs without a target user."""
    return "!anonymous"
