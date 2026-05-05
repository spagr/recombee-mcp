"""Verify package metadata."""

from recombee_mcp import __version__


def test_version_is_string():
    assert isinstance(__version__, str)
    assert __version__ == "0.1.0"
