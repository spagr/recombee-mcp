"""FastMCP server instance and entry point."""

import sys
from typing import Any

import structlog

from recombee_mcp import __version__
from recombee_mcp.audit import AuditLogger
from recombee_mcp.client import create_client
from recombee_mcp.settings import Settings

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(20),
    logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
)

log = structlog.get_logger()


def create_server() -> Any:
    """Create and configure the FastMCP server with all tools registered."""
    from fastmcp import FastMCP

    from recombee_mcp.tools.catalog import register_catalog_tools
    from recombee_mcp.tools.meta import register_meta_tools
    from recombee_mcp.tools.recommendations import register_recommendation_tools
    from recombee_mcp.tools.search import register_search_tools
    from recombee_mcp.tools.segments import register_segment_tools

    settings = Settings()  # type: ignore[call-arg]
    client = create_client(settings)
    audit = AuditLogger(log_dir=settings.audit_log_dir)

    mcp = FastMCP(
        "recombee-mcp",
        version=__version__,
        instructions=(
            "Recombee recommendation engine MCP server. "
            f"Profile: {settings.profile}, Region: {settings.region}, "
            f"Database: {settings.db_id}. "
            "All tools are read-only unless explicitly noted."
        ),
    )

    ctx = ServerContext(settings=settings, client=client, audit=audit)

    register_meta_tools(mcp, ctx)
    register_catalog_tools(mcp, ctx)
    register_recommendation_tools(mcp, ctx)
    register_search_tools(mcp, ctx)
    register_segment_tools(mcp, ctx)

    log.info(
        "server_configured",
        profile=settings.profile,
        region=settings.region,
        db_id=settings.db_id,
        version=__version__,
    )

    return mcp


class ServerContext:
    """Shared context passed to all tool registration functions."""

    def __init__(self, settings: Settings, client: Any, audit: AuditLogger) -> None:
        self.settings = settings
        self.client = client
        self.audit = audit


def main() -> None:
    """Start the Recombee MCP server."""
    mcp = create_server()
    mcp.run(transport="stdio")
