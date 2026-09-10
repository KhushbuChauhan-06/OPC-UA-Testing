"""Integration and negative tests for simulated motor methods."""

from __future__ import annotations

from collections.abc import Callable

import pytest
from asyncua import ua

from opcua_framework.client import OPCUAClientError, OPCUATestClient
from opcua_framework.server import OPCUATestServer


@pytest.mark.functional
async def test_start_and_stop_motor_methods_change_expected_state(
    opcua_client: OPCUATestClient, plant_path: Callable[..., list[str]]
) -> None:
    control = await opcua_client.get_node_by_path(plant_path("Control"))
    start_motor = await opcua_client.get_node_by_path(plant_path("Control", "StartMotor"))
    stop_motor = await opcua_client.get_node_by_path(plant_path("Control", "StopMotor"))
    status = await opcua_client.get_node_by_path(plant_path("Motor", "Status"))
    speed = await opcua_client.get_node_by_path(plant_path("Motor", "Speed"))

    await opcua_client.call_method(control, start_motor)
    assert await opcua_client.read_value(status) == "RUNNING"
    assert await opcua_client.read_value(speed) > 0

    await opcua_client.call_method(control, stop_motor)
    assert await opcua_client.read_value(status) == "STOPPED"
    assert await opcua_client.read_value(speed) == 0


@pytest.mark.negative
async def test_invalid_method_is_reported_by_the_server(
    opcua_client: OPCUATestClient,
    opcua_server: OPCUATestServer,
    plant_path: Callable[..., list[str]],
) -> None:
    control = await opcua_client.get_node_by_path(plant_path("Control"))
    invalid_method = ua.NodeId("NotAMethod", opcua_server.namespace_index)

    with pytest.raises(OPCUAClientError, match="call OPC UA method"):
        await opcua_client.call_method(control, invalid_method)


@pytest.mark.negative
async def test_incorrect_speed_data_type_is_rejected(
    opcua_client: OPCUATestClient, plant_path: Callable[..., list[str]]
) -> None:
    speed = await opcua_client.get_node_by_path(plant_path("Motor", "Speed"))

    with pytest.raises(OPCUAClientError, match="write OPC UA value"):
        await opcua_client.write_value(speed, "fast", ua.VariantType.Int32)
