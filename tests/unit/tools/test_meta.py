"""Tests for meta tools."""

from unittest.mock import MagicMock

import pytest
from recombee_api_client.exceptions import APIException

from recombee_mcp.errors import ToolError
from recombee_mcp.server import ServerContext
from recombee_mcp.tools.meta import register_meta_tools
from tests.conftest import get_tool


def test_describe_setup_happy_path(mcp, ctx: ServerContext):
    ctx.client.send = MagicMock(
        side_effect=[
            [{"name": "title", "type": "string"}, {"name": "price", "type": "double"}],
            [{"name": "name", "type": "string"}],
        ]
    )
    register_meta_tools(mcp, ctx)
    tool = get_tool(mcp, "describe_setup")
    result = tool.fn()

    assert result["server_version"] == "0.1.0"
    assert result["profile"] == "sandbox"
    assert result["database_id"] == "test-db"
    assert result["item_property_count"] == 2
    assert result["user_property_count"] == 1
    assert result["writes_allowed"] is False


def test_describe_setup_api_error(mcp, ctx: ServerContext):
    ctx.client.send = MagicMock(side_effect=APIException(404, "Not found"))
    register_meta_tools(mcp, ctx)
    tool = get_tool(mcp, "describe_setup")

    with pytest.raises(ToolError, match="describe_setup"):
        tool.fn()
