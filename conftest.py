"""Shared pytest configuration for the OPC UA test suite."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator, Callable

import pytest
import pytest_asyncio

from opcua_framework.client import OPCUATestClient
from opcua_framework.server import OPCUATestServer
from opcua_framework.config import load_settings


def pytest_configure() -> None:
    """Set a consistent baseline for framework loggers during test runs."""
    logging.getLogger("opcua_framework").setLevel(logging.INFO)
    logging.getLogger("asyncua").setLevel(logging.WARNING)
    from pathlib import Path

    Path("logs").mkdir(exist_ok=True)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    if not any(getattr(handler, "_opcua_framework_log", False) for handler in root_logger.handlers):
        file_handler = logging.FileHandler("logs/test-run.log", encoding="utf-8")
        file_handler._opcua_framework_log = True  # type: ignore[attr-defined]
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"))
        root_logger.addHandler(file_handler)


@pytest_asyncio.fixture
async def opcua_server() -> AsyncIterator[OPCUATestServer]:
    """Start an isolated local OPC UA server for one test."""
    settings = load_settings()["opcua"]
    server = OPCUATestServer(
        endpoint=settings["endpoint"], simulation_interval_seconds=settings["simulation_interval_seconds"]
    )
    await server.start()
    try:
        yield server
    finally:
        await server.stop()


@pytest_asyncio.fixture
async def opcua_client(opcua_server: OPCUATestServer) -> AsyncIterator[OPCUATestClient]:
    """Provide a connected client and guarantee session cleanup after a test."""
    client = OPCUATestClient(opcua_server.endpoint, timeout_seconds=load_settings()["opcua"]["client_timeout_seconds"])
    await client.connect()
    try:
        yield client
    finally:
        await client.disconnect()


@pytest.fixture
def plant_path(opcua_server: OPCUATestServer) -> Callable[..., list[str]]:
    """Build namespace-qualified browse paths for the simulated plant contract."""
    namespace_index = opcua_server.namespace_index

    def build_path(*node_names: str) -> list[str]:
        return [
            f"{namespace_index}:IndustrialPlant",
            *[f"{namespace_index}:{name}" for name in node_names],
        ]

    return build_path
