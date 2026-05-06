"""Recombee API client factory."""

from recombee_api_client.api_client import RecombeeClient, Region

from recombee_mcp.settings import Settings

REGION_MAP = {
    "eu-west": Region.EU_WEST,
    "us-west": Region.US_WEST,
    "ap-se": Region.AP_SE,
    "ca-east": Region.CA_EAST,
}


def create_client(settings: Settings) -> RecombeeClient:
    """Create and return a configured RecombeeClient instance."""
    return RecombeeClient(
        settings.db_id,
        settings.private_token.get_secret_value(),
        region=REGION_MAP[settings.region],
    )
