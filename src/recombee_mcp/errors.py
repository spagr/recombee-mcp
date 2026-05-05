"""Custom exception hierarchy for the Recombee MCP server."""


class RecombeMcpError(Exception):
    """Base exception for all recombee-mcp errors."""


class ConfigurationError(RecombeMcpError):
    """Raised when server configuration is invalid or missing."""


class ToolError(RecombeMcpError):
    """Raised when a tool execution fails in a way the LLM should see."""

    def __init__(self, tool_name: str, message: str) -> None:
        self.tool_name = tool_name
        super().__init__(f"[{tool_name}] {message}")


class ReqlValidationError(RecombeMcpError):
    """Raised when a user-supplied ReQL filter fails validation."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Invalid ReQL filter: {reason}")
