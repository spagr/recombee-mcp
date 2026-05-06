"""Segment tools — segmentations and segment recommendations."""

from typing import Any

from recombee_api_client.api_requests import (
    ListSegmentations,
    RecommendItemSegmentsToUser,
)
from recombee_api_client.exceptions import APIException

from recombee_mcp.errors import ToolError


def register_segment_tools(mcp: Any, ctx: Any) -> None:
    """Register segment tools with the MCP server."""

    @mcp.tool()
    def list_segmentations(
        source_type: str = "items",
    ) -> dict[str, Any]:
        """List all configured segmentations in the database.

        Segmentations group items into segments (e.g., categories, brands).
        Use this to discover what segmentations are available before requesting
        segment-level recommendations.

        Args:
            source_type: One of "items", "users", "interactions" (default: "items").
        """
        ctx.audit.log(
            profile=ctx.settings.profile,
            db_id=ctx.settings.db_id,
            tool_name="list_segmentations",
            parameters={"source_type": source_type},
            outcome="success",
        )
        try:
            result = ctx.client.send(ListSegmentations(source_type))
        except APIException as e:
            raise ToolError("list_segmentations", str(e)) from e
        return {"database_id": ctx.settings.db_id, "segmentations": result}

    @mcp.tool()
    def recommend_segments_to_user(
        user_id: str,
        count: int = 5,
        scenario: str | None = None,
        filter: str | None = None,  # noqa: A002
        booster: str | None = None,
    ) -> dict[str, Any]:
        """Recommend top item segments (categories, brands) for a user.

        Returns the segments most relevant to the user based on their interaction history.

        Args:
            user_id: The user to get segment recommendations for.
            count: Number of segments to recommend (1-50).
            scenario: Scenario name for context-specific recommendations.
            filter: ReQL filter expression to narrow results.
            booster: ReQL booster expression to influence ranking.
        """
        count = min(max(count, 1), 50)
        params: dict[str, Any] = {"user_id": user_id, "count": count}
        if scenario:
            params["scenario"] = scenario

        ctx.audit.log(
            profile=ctx.settings.profile,
            db_id=ctx.settings.db_id,
            tool_name="recommend_segments_to_user",
            parameters=params,
            outcome="success",
        )
        try:
            request = RecommendItemSegmentsToUser(
                user_id,
                count,
                scenario=scenario,
                filter=filter or None,
                booster=booster or None,
            )
            result = ctx.client.send(request)
        except APIException as e:
            raise ToolError("recommend_segments_to_user", str(e)) from e
        return {
            "database_id": ctx.settings.db_id,
            "user_id": user_id,
            "recomm_id": result.get("recommId"),
            "recomms": result.get("recomms", []),
        }
