"""Framework configuration loaded from YAML with safe environment overrides."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "framework.yaml"


@lru_cache(maxsize=1)
def load_settings(config_path: Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    """Load non-secret framework settings and apply the endpoint override."""
    with config_path.open(encoding="utf-8") as config_file:
        settings: dict[str, Any] = yaml.safe_load(config_file)
    settings["opcua"]["endpoint"] = os.getenv("OPCUA_ENDPOINT", settings["opcua"]["endpoint"])
    return settings
