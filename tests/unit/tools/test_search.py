"""Tests for search tools."""

from unittest.mock import MagicMock

import pytest
from recombee_api_client.exceptions import APIException

from recombee_mcp.errors import ToolError
from recombee_mcp.server import ServerContext
from recombee_mcp.tools.search import register_search_tools
from tests.conftest import get_tool


@pytest.fixture(autouse=True)
def _register(mcp, ctx):
    register_search_tools(mcp, ctx)


def test_search_items_happy_path(mcp, ctx: ServerContext):
    ctx.client.send = MagicMock(
        return_value={
            "recommId": "search-1",
            "recomms": [{"id": "item-1", "values": {"title": "Chef Knife"}}],
        }
    )
    tool = get_tool(mcp, "search_items")
    result = tool.fn(user_id="u1", search_query="knife")

    assert result["search_query"] == "knife"
    assert result["recomm_id"] == "search-1"
    assert len(result["recomms"]) == 1


def test_search_items_api_error(mcp, ctx: ServerContext):
    ctx.client.send = MagicMock(side_effect=APIException(500, "Internal error"))
    tool = get_tool(mcp, "search_items")

    with pytest.raises(ToolError, match="search_items"):
        tool.fn(user_id="u1", search_query="pan")
