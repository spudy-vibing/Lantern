"""Basic tests for package metadata."""

from lantern import __app_name__, __version__


def test_version():
    """Test that version is defined."""
    assert __version__ == "0.1.0"


def test_app_name():
    """Test that app name is defined."""
    assert __app_name__ == "lantern"
