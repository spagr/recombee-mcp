"""Meta/diagnostic tools for the Recombee MCP server."""

from typing import Any

from recombee_api_client.api_requests import ListItemProperties, ListUserProperties
from recombee_api_client.exceptions import APIException

from recombee_mcp import __version__
from recombee_mcp.errors import ToolError


def register_meta_tools(mcp: Any, ctx: Any) -> None:
    """Register meta/diagnostic tools with the MCP server."""

    @mcp.tool()
    def describe_setup() -> dict[str, Any]:
        """Return the current server configuration and database schema overview.

        Use this tool at the start of a session to understand what database you're
        connected to, what properties exist, and what tools are available.
        Does NOT return the API token — only safe metadata.
        """
        ctx.audit.log(
            profile=ctx.settings.profile,
            db_id=ctx.settings.db_id,
            tool_name="describe_setup",
            parameters={},
            outcome="success",
        )

        try:
            item_props = ctx.client.send(ListItemProperties())
            user_props = ctx.client.send(ListUserProperties())
        except APIException as e:
            raise ToolError("describe_setup", f"Failed to fetch schema: {e}") from e

        return {
            "server_version": __version__,
            "profile": ctx.settings.profile,
            "region": ctx.settings.region,
            "database_id": ctx.settings.db_id,
            "writes_allowed": ctx.settings.writes_allowed,
            "item_properties": [{"name": p["name"], "type": p["type"]} for p in item_props],
            "user_properties": [{"name": p["name"], "type": p["type"]} for p in user_props],
            "item_property_count": len(item_props),
            "user_property_count": len(user_props),
        }
