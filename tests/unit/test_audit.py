"""Tests for audit logger."""

import json
from pathlib import Path

from recombee_mcp.audit import AuditLogger, _truncate_params


def test_audit_logger_creates_file(tmp_path: Path):
    logger = AuditLogger(log_dir=tmp_path)
    assert logger.log_path == tmp_path / "audit.log"

    logger.log(
        profile="sandbox",
        db_id="test-db",
        tool_name="recommend_to_user",
        parameters={"user_id": "u1", "count": 10},
        outcome="success",
    )

    lines = logger.log_path.read_text().strip().split("\n")
    assert len(lines) == 1

    entry = json.loads(lines[0])
    assert entry["profile"] == "sandbox"
    assert entry["db_id"] == "test-db"
    assert entry["tool"] == "recommend_to_user"
    assert entry["parameters"] == {"user_id": "u1", "count": 10}
    assert entry["outcome"] == "success"
    assert "timestamp" in entry
    assert "iso_time" in entry
    assert "error" not in entry


def test_audit_logger_with_error(tmp_path: Path):
    logger = AuditLogger(log_dir=tmp_path)
    logger.log(
        profile="production",
        db_id="prod-db",
        tool_name="get_item_properties",
        parameters={"item_id": "i1"},
        outcome="error",
        error="Item not found",
    )

    entry = json.loads(logger.log_path.read_text().strip())
    assert entry["outcome"] == "error"
    assert entry["error"] == "Item not found"


def test_audit_logger_appends(tmp_path: Path):
    logger = AuditLogger(log_dir=tmp_path)
    for i in range(3):
        logger.log(
            profile="sandbox",
            db_id="db",
            tool_name=f"tool_{i}",
            parameters={},
            outcome="success",
        )

    lines = logger.log_path.read_text().strip().split("\n")
    assert len(lines) == 3


def test_truncate_params_short_values():
    params = {"key": "short", "num": 42}
    assert _truncate_params(params) == params


def test_truncate_params_long_string():
    long_val = "x" * 300
    result = _truncate_params({"filter": long_val})
    assert len(result["filter"]) == 203  # 200 + "..."
    assert result["filter"].endswith("...")
