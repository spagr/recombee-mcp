"""Catalog inspection tools — item and user properties."""

from typing import Any

from recombee_api_client.api_requests import (
    GetItemValues,
    GetUserValues,
    ListItemProperties,
    ListItems,
    ListUserProperties,
)
from recombee_api_client.exceptions import APIException

from recombee_mcp.errors import ToolError


def register_catalog_tools(mcp: Any, ctx: Any) -> None:
    """Register catalog inspection tools with the MCP server."""

    @mcp.tool()
    def get_item_properties(item_id: str) -> dict[str, Any]:
        """Get all property values for a single item.

        Returns all stored properties and their current values for the specified item.
        Useful for inspecting data quality or understanding what data Recombee has about an item.
        """
        ctx.audit.log(
            profile=ctx.settings.profile,
            db_id=ctx.settings.db_id,
            tool_name="get_item_properties",
            parameters={"item_id": item_id},
            outcome="success",
        )
        try:
            result = ctx.client.send(GetItemValues(item_id))
        except APIException as e:
            raise ToolError("get_item_properties", str(e)) from e
        return {"item_id": item_id, "database_id": ctx.settings.db_id, "properties": result}

    @mcp.tool()
    def list_items(
        count: int = 25,
        offset: int = 0,
        filter: str | None = None,  # noqa: A002
    ) -> dict[str, Any]:
        """List item IDs from the database with optional filtering.

        Args:
            count: Number of items to return (max 100).
            offset: Pagination offset.
            filter: Optional ReQL filter expression (e.g. '"category" == "knives"').
        """
        count = min(count, 100)
        params: dict[str, Any] = {"count": count, "offset": offset}
        if filter:
            params["filter"] = filter

        ctx.audit.log(
            profile=ctx.settings.profile,
            db_id=ctx.settings.db_id,
            tool_name="list_items",
            parameters=params,
            outcome="success",
        )
        try:
            request = ListItems(count=count, offset=offset, filter=filter or None)
            result = ctx.client.send(request)
        except APIException as e:
            raise ToolError("list_items", str(e)) from e
        return {"database_id": ctx.settings.db_id, "items": result, "count": len(result)}

    @mcp.tool()
    def list_item_properties() -> dict[str, Any]:
        """List the schema of all item properties in the database.

        Returns property names and their types. Use this to understand what data
        fields are available for items before querying specific items or building filters.
        """
        ctx.audit.log(
            profile=ctx.settings.profile,
            db_id=ctx.settings.db_id,
            tool_name="list_item_properties",
            parameters={},
            outcome="success",
        )
        try:
            result = ctx.client.send(ListItemProperties())
        except APIException as e:
            raise ToolError("list_item_properties", str(e)) from e
        return {"database_id": ctx.settings.db_id, "properties": result}

    @mcp.tool()
    def list_user_properties() -> dict[str, Any]:
        """List the schema of all user properties in the database.

        Returns property names and their types. Use this to understand what data
        fields are available for users.
        """
        ctx.audit.log(
            profile=ctx.settings.profile,
            db_id=ctx.settings.db_id,
            tool_name="list_user_properties",
            parameters={},
            outcome="success",
        )
        try:
            result = ctx.client.send(ListUserProperties())
        except APIException as e:
            raise ToolError("list_user_properties", str(e)) from e
        return {"database_id": ctx.settings.db_id, "properties": result}

    @mcp.tool()
    def get_user_properties(user_id: str) -> dict[str, Any]:
        """Get all property values for a single user.

        Returns all stored properties and their current values for the specified user.
        """
        ctx.audit.log(
            profile=ctx.settings.profile,
            db_id=ctx.settings.db_id,
            tool_name="get_user_properties",
            parameters={"user_id": user_id},
            outcome="success",
        )
        try:
            result = ctx.client.send(GetUserValues(user_id))
        except APIException as e:
            raise ToolError("get_user_properties", str(e)) from e
        return {"user_id": user_id, "database_id": ctx.settings.db_id, "properties": result}
