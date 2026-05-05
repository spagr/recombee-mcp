"""Tests for settings module."""

import pytest
from pydantic import ValidationError

from recombee_mcp.settings import Settings


def test_settings_minimal_valid():
    s = Settings(db_id="test-db", private_token="secret-token")
    assert s.db_id == "test-db"
    assert s.private_token.get_secret_value() == "secret-token"
    assert s.region == "eu-west"
    assert s.profile == "production"
    assert s.write_enabled is False
    assert s.log_level == "INFO"
    assert s.batch_max_size == 100


def test_settings_writes_allowed_production_disabled():
    s = Settings(db_id="x", private_token="x", profile="production", write_enabled=True)
    assert s.writes_allowed is False


def test_settings_writes_allowed_sandbox_enabled():
    s = Settings(db_id="x", private_token="x", profile="sandbox", write_enabled=True)
    assert s.writes_allowed is True


def test_settings_writes_allowed_sandbox_disabled():
    s = Settings(db_id="x", private_token="x", profile="sandbox", write_enabled=False)
    assert s.writes_allowed is False


def test_settings_invalid_region():
    with pytest.raises(ValidationError):
        Settings(db_id="x", private_token="x", region="invalid")


def test_settings_invalid_profile():
    with pytest.raises(ValidationError):
        Settings(db_id="x", private_token="x", profile="staging")


def test_settings_missing_required_field():
    with pytest.raises(ValidationError):
        Settings(db_id="x")  # type: ignore[call-arg]


def test_settings_extra_fields_forbidden():
    with pytest.raises(ValidationError):
        Settings(db_id="x", private_token="x", unknown_field="y")
