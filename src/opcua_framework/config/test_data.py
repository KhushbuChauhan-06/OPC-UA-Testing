"""Central test-data constants derived from the framework configuration."""

from __future__ import annotations

from .settings import load_settings

SETTINGS = load_settings()
SENSOR_EXPECTATIONS = SETTINGS["sensors"]
TEST_VALUES = SETTINGS["test_values"]
