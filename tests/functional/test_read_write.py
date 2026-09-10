"""Read, write, data-validation, and invalid-operation integration tests."""

from __future__ import annotations

from collections.abc import Callable

import pytest
from asyncua import ua

from opcua_framework.client import OPCUAClientError, OPCUATestClient
from opcua_framework.config.test_data import SENSOR_EXPECTATIONS, TEST_VALUES


@pytest.mark.functional
@pytest.mark.parametrize(
    ("sensor_name", "minimum", "maximum"),
    [(name, values["minimum"], values["maximum"]) for name, values in SENSOR_EXPECTATIONS.items()],
)
async def test_sensor_values_are_typed_and_within_simulated_ranges(
    opcua_client: OPCUATestClient,
    plant_path: Callable[..., list[str]],
    sensor_name: str,
    minimum: float,
    maximum: float,
) -> None:
    sensor = await opcua_client.get_node_by_path(plant_path("Sensors", sensor_name))
    value = await opcua_client.read_value(sensor)

    assert isinstance(value, float)
    assert minimum <= value <= maximum


@pytest.mark.functional
async def test_writable_motor_speed_can_be_read_back(
    opcua_client: OPCUATestClient, plant_path: Callable[..., list[str]]
) -> None:
    speed = await opcua_client.get_node_by_path(plant_path("Motor", "Speed"))

    await opcua_client.write_value(speed, TEST_VALUES["motor_speed"], ua.VariantType.Int32)

    assert await opcua_client.read_value(speed) == TEST_VALUES["motor_speed"]


@pytest.mark.negative
async def test_invalid_node_path_raises_meaningful_client_error(
    opcua_client: OPCUATestClient, plant_path: Callable[..., list[str]]
) -> None:
    with pytest.raises(OPCUAClientError, match="browse path"):
        await opcua_client.get_node_by_path(plant_path("Sensors", "NotARealSensor"))


@pytest.mark.negative
async def test_writing_read_only_sensor_raises_meaningful_client_error(
    opcua_client: OPCUATestClient, plant_path: Callable[..., list[str]]
) -> None:
    temperature = await opcua_client.get_node_by_path(plant_path("Sensors", "Temperature"))

    with pytest.raises(OPCUAClientError, match="write OPC UA value"):
        await opcua_client.write_value(temperature, 99.0, ua.VariantType.Float)
