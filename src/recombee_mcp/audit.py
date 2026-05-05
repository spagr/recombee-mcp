"""JSONL audit logger for tool calls."""

import json
import time
from pathlib import Path
from typing import Any

import platformdirs


def get_default_audit_dir() -> Path:
    """Return the platform-specific default audit log directory."""
    return Path(platformdirs.user_data_dir("recombee-mcp", ensure_exists=True))


class AuditLogger:
    """Writes one JSONL line per tool call to the audit log."""

    def __init__(self, log_dir: Path | None = None) -> None:
        self._log_dir = log_dir or get_default_audit_dir()
        self._log_dir.mkdir(parents=True, exist_ok=True)
        self._log_path = self._log_dir / "audit.log"

    @property
    def log_path(self) -> Path:
        """Path to the audit log file."""
        return self._log_path

    def log(
        self,
        *,
        profile: str,
        db_id: str,
        tool_name: str,
        parameters: dict[str, Any],
        outcome: str,
        error: str | None = None,
    ) -> None:
        """Append a single audit entry."""
        entry = {
            "timestamp": time.time(),
            "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "profile": profile,
            "db_id": db_id,
            "tool": tool_name,
            "parameters": _truncate_params(parameters),
            "outcome": outcome,
        }
        if error:
            entry["error"] = error[:500]

        with self._log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _truncate_params(params: dict[str, Any], max_str_len: int = 200) -> dict[str, Any]:
    """Truncate long string values in parameters for audit logging."""
    result: dict[str, Any] = {}
    for key, value in params.items():
        if isinstance(value, str) and len(value) > max_str_len:
            result[key] = value[:max_str_len] + "..."
        else:
            result[key] = value
    return result
