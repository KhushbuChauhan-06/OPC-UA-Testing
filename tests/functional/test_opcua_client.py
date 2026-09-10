"""Focused integration tests for the reusable OPC UA client wrapper."""

from __future__ import annotations

import pytest
from asyncua import ua
from collections.abc import Callable

from opcua_framework.client import OPCUAClientError, OPCUATestClient


@pytest.mark.functional
async def test_client_connects_and_disconnects(opcua_client: OPCUATestClient) -> None:
    assert opcua_client.is_connected()

    await opcua_client.disconnect()
    assert not opcua_client.is_connected()


@pytest.mark.functional
async def test_client_browses_reads_and_writes(
    opcua_client: OPCUATestClient, plant_path: Callable[..., list[str]]
) -> None:
    client = opcua_client

    objects = await client.browse()
    browse_names = []
    for node in objects:
        browse_names.append((await node.read_browse_name()).Name)
    assert "IndustrialPlant" in browse_names

    temperature = await client.get_node_by_path(plant_path("Sensors", "Temperature"))
    assert isinstance(await client.read_value(temperature), float)

    speed = await client.get_node_by_path(plant_path("Motor", "Speed"))
    await client.write_value(speed, 800, ua.VariantType.Int32)
    assert await client.read_value(speed) == 800


@pytest.mark.functional
async def test_client_calls_motor_methods(
    opcua_client: OPCUATestClient, plant_path: Callable[..., list[str]]
) -> None:
    client = opcua_client

    motor = await client.get_node_by_path(plant_path("Motor"))
    control = await client.get_node_by_path(plant_path("Control"))
    start_motor = await client.get_node_by_path(plant_path("Control", "StartMotor"))
    stop_motor = await client.get_node_by_path(plant_path("Control", "StopMotor"))
    status = await client.get_node_by_path(plant_path("Motor", "Status"))
    speed = await client.get_node_by_path(plant_path("Motor", "Speed"))

    await client.call_method(control, start_motor)
    assert await client.read_value(status) == "RUNNING"
    assert await client.read_value(speed) > 0

    await client.call_method(control, stop_motor)
    assert await client.read_value(status) == "STOPPED"
    assert await client.read_value(speed) == 0


@pytest.mark.negative
async def test_client_reports_operations_when_disconnected() -> None:
    client = OPCUATestClient("opc.tcp://127.0.0.1:4840/abb-test-server/")

    with pytest.raises(OPCUAClientError, match="not connected"):
        await client.read_value("ns=2;s=Temperature")


@pytest.mark.negative
async def test_failed_connection_leaves_client_disconnected() -> None:
    client = OPCUATestClient("opc.tcp://127.0.0.1:49999/no-server/", timeout_seconds=0.1)

    with pytest.raises(OPCUAClientError, match="Unable to connect"):
        await client.connect()

    assert not client.is_connected()
