"""Tests for catalog tools."""

from unittest.mock import MagicMock

import pytest
from recombee_api_client.exceptions import APIException

from recombee_mcp.errors import ToolError
from recombee_mcp.server import ServerContext
from recombee_mcp.tools.catalog import register_catalog_tools
from tests.conftest import get_tool


@pytest.fixture(autouse=True)
def _register(mcp, ctx):
    register_catalog_tools(mcp, ctx)


def test_get_item_properties_happy_path(mcp, ctx: ServerContext):
    ctx.client.send = MagicMock(return_value={"title": "Knife", "price": 29.99})
    tool = get_tool(mcp, "get_item_properties")
    result = tool.fn(item_id="item-1")

    assert result["item_id"] == "item-1"
    assert result["properties"]["title"] == "Knife"
    assert result["database_id"] == "test-db"


def test_get_item_properties_not_found(mcp, ctx: ServerContext):
    ctx.client.send = MagicMock(side_effect=APIException(404, "Item not found"))
    tool = get_tool(mcp, "get_item_properties")

    with pytest.raises(ToolError, match="get_item_properties"):
        tool.fn(item_id="nonexistent")


def test_list_items_happy_path(mcp, ctx: ServerContext):
    ctx.client.send = MagicMock(return_value=["item-1", "item-2", "item-3"])
    tool = get_tool(mcp, "list_items")
    result = tool.fn(count=3)

    assert result["count"] == 3
    assert result["items"] == ["item-1", "item-2", "item-3"]


def test_list_items_count_capped_at_100(mcp, ctx: ServerContext):
    ctx.client.send = MagicMock(return_value=[])
    tool = get_tool(mcp, "list_items")
    tool.fn(count=200)

    call_args = ctx.client.send.call_args[0][0]
    assert call_args.count == 100


def test_list_item_properties_happy_path(mcp, ctx: ServerContext):
    ctx.client.send = MagicMock(return_value=[{"name": "title", "type": "string"}])
    tool = get_tool(mcp, "list_item_properties")
    result = tool.fn()
    assert result["properties"] == [{"name": "title", "type": "string"}]


def test_get_user_properties_happy_path(mcp, ctx: ServerContext):
    ctx.client.send = MagicMock(return_value={"name": "John", "country": "CZ"})
    tool = get_tool(mcp, "get_user_properties")
    result = tool.fn(user_id="user-1")

    assert result["user_id"] == "user-1"
    assert result["properties"]["name"] == "John"
