"""Recombee API client factory."""

from recombee_api_client.api_client import RecombeeClient

from recombee_mcp.settings import Settings

REGION_MAP = {
    "eu-west": "client-rapi-eu-west.recombee.com",
    "us-west": "client-rapi-us-west.recombee.com",
    "ap-se": "client-rapi-ap-se.recombee.com",
    "ca-east": "client-rapi-ca-east.recombee.com",
}


def create_client(settings: Settings) -> RecombeeClient:
    """Create and return a configured RecombeeClient instance."""
    region_host = REGION_MAP[settings.region]
    return RecombeeClient(
        settings.db_id,
        settings.private_token.get_secret_value(),
        region=region_host,
    )
