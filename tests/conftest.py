"""Shared test fixtures."""

import asyncio
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from recombee_mcp.audit import AuditLogger
from recombee_mcp.server import ServerContext
from recombee_mcp.settings import Settings


@pytest.fixture(autouse=True)
def _isolate_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Isolate tests from any local .env file or RECOMBEE_* env vars.

    Ensures Settings() in tests behaves identically on dev machines and CI,
    regardless of the developer's real Recombee credentials.
    """
    for var in list(__import__("os").environ):
        if var.startswith("RECOMBEE_"):
            monkeypatch.delenv(var, raising=False)
    monkeypatch.chdir(tmp_path)


@pytest.fixture
def settings() -> Settings:
    return Settings(db_id="test-db", private_token="test-token", profile="sandbox")


@pytest.fixture
def mock_client() -> MagicMock:
    return MagicMock()


@pytest.fixture
def audit_logger(tmp_path: Path) -> AuditLogger:
    return AuditLogger(log_dir=tmp_path)


@pytest.fixture
def ctx(settings: Settings, mock_client: MagicMock, audit_logger: AuditLogger) -> ServerContext:
    return ServerContext(settings=settings, client=mock_client, audit=audit_logger)


@pytest.fixture
def mcp(ctx: ServerContext) -> Any:
    from fastmcp import FastMCP

    server = FastMCP("test")
    return server


def get_tool(mcp: Any, name: str) -> Any:
    """Helper to synchronously get a registered tool from FastMCP."""
    return asyncio.run(mcp.get_tool(name))
