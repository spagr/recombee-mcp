"""Application settings loaded from environment variables and .env file."""

from pathlib import Path
from typing import Literal

from pydantic import PositiveInt, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Recombee MCP server configuration."""

    model_config = SettingsConfigDict(
        env_prefix="RECOMBEE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
    )

    db_id: str
    private_token: SecretStr
    region: Literal["eu-west", "us-west", "ap-se", "ca-east"] = "eu-west"
    profile: Literal["production", "sandbox"] = "production"
    write_enabled: bool = False
    integration_db_id: str | None = None
    integration_token: SecretStr | None = None
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    audit_log_dir: Path | None = None
    batch_max_size: PositiveInt = 100

    @property
    def writes_allowed(self) -> bool:
        """Write tools are only available in sandbox profile with write_enabled=True."""
        return self.profile == "sandbox" and self.write_enabled
