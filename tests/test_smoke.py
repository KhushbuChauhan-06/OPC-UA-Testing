"""Smoke checks for the test environment and installed package."""

import pytest

from opcua_framework import __version__


@pytest.mark.smoke
def test_framework_package_is_importable() -> None:
    """Verify that Pytest can import the installed framework package."""
    assert __version__ == "0.1.0"
