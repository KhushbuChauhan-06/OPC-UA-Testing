"""Connection-level integration tests for the local OPC UA endpoint."""

from __future__ import annotations

import pytest

from opcua_framework.client import OPCUATestClient


@pytest.mark.smoke
@pytest.mark.functional
async def test_valid_connection_is_established(opcua_client: OPCUATestClient) -> None:
    assert opcua_client.is_connected()


@pytest.mark.functional
async def test_server_objects_root_is_accessible(opcua_client: OPCUATestClient) -> None:
    root_children = await opcua_client.browse()
    browse_names = [(await node.read_browse_name()).Name for node in root_children]

    assert "IndustrialPlant" in browse_names


@pytest.mark.functional
async def test_disconnect_is_clean(opcua_client: OPCUATestClient) -> None:
    await opcua_client.disconnect()

    assert not opcua_client.is_connected()
