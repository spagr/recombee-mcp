"""Tests for recommendation tools."""

from unittest.mock import MagicMock

import pytest
from recombee_api_client.exceptions import APIException

from recombee_mcp.errors import ToolError
from recombee_mcp.server import ServerContext
from recombee_mcp.tools.recommendations import register_recommendation_tools
from tests.conftest import get_tool


@pytest.fixture(autouse=True)
def _register(mcp, ctx):
    register_recommendation_tools(mcp, ctx)


def test_recommend_to_user_happy_path(mcp, ctx: ServerContext):
    ctx.client.send = MagicMock(
        return_value={
            "recommId": "rec-123",
            "recomms": [{"id": "item-1", "values": {"title": "Knife"}}],
        }
    )
    tool = get_tool(mcp, "recommend_to_user")
    result = tool.fn(user_id="u1", count=5, scenario="homepage")

    assert result["user_id"] == "u1"
    assert result["recomm_id"] == "rec-123"
    assert len(result["recomms"]) == 1
    assert result["scenario"] == "homepage"


def test_recommend_to_user_api_error(mcp, ctx: ServerContext):
    ctx.client.send = MagicMock(side_effect=APIException(400, "Bad request"))
    tool = get_tool(mcp, "recommend_to_user")

    with pytest.raises(ToolError, match="recommend_to_user"):
        tool.fn(user_id="u1")


def test_recommend_to_item_happy_path(mcp, ctx: ServerContext):
    ctx.client.send = MagicMock(
        return_value={
            "recommId": "rec-456",
            "recomms": [{"id": "item-2"}],
        }
    )
    tool = get_tool(mcp, "recommend_to_item")
    result = tool.fn(item_id="item-1", target_user_id="u1")

    assert result["item_id"] == "item-1"
    assert result["recomm_id"] == "rec-456"


def test_recommend_next_items_happy_path(mcp, ctx: ServerContext):
    ctx.client.send = MagicMock(
        return_value={
            "recommId": "rec-789",
            "recomms": [{"id": "item-3"}],
        }
    )
    tool = get_tool(mcp, "recommend_next_items")
    result = tool.fn(recomm_id="rec-123", count=5)

    assert result["recomm_id"] == "rec-789"


def test_recommend_to_user_count_clamped(mcp, ctx: ServerContext):
    ctx.client.send = MagicMock(return_value={"recommId": "r", "recomms": []})
    tool = get_tool(mcp, "recommend_to_user")
    tool.fn(user_id="u1", count=200)

    call_args = ctx.client.send.call_args[0][0]
    assert call_args.count == 100
