"""Tests for segment tools."""

from unittest.mock import MagicMock

import pytest
from recombee_api_client.exceptions import APIException

from recombee_mcp.errors import ToolError
from recombee_mcp.server import ServerContext
from recombee_mcp.tools.segments import register_segment_tools
from tests.conftest import get_tool


@pytest.fixture(autouse=True)
def _register(mcp, ctx):
    register_segment_tools(mcp, ctx)


def test_list_segmentations_happy_path(mcp, ctx: ServerContext):
    ctx.client.send = MagicMock(
        return_value=[{"segmentationId": "category", "sourceType": "item-property"}]
    )
    tool = get_tool(mcp, "list_segmentations")
    result = tool.fn()

    assert result["database_id"] == "test-db"
    assert len(result["segmentations"]) == 1


def test_list_segmentations_api_error(mcp, ctx: ServerContext):
    ctx.client.send = MagicMock(side_effect=APIException(403, "Forbidden"))
    tool = get_tool(mcp, "list_segmentations")

    with pytest.raises(ToolError, match="list_segmentations"):
        tool.fn()


def test_recommend_segments_to_user_happy_path(mcp, ctx: ServerContext):
    ctx.client.send = MagicMock(
        return_value={
            "recommId": "seg-1",
            "recomms": [{"id": "category-knives"}],
        }
    )
    tool = get_tool(mcp, "recommend_segments_to_user")
    result = tool.fn(user_id="u1", count=3)

    assert result["user_id"] == "u1"
    assert result["recomm_id"] == "seg-1"
