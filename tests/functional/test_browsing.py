"""Address-space browsing integration tests."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from opcua_framework.client import OPCUATestClient


@pytest.mark.functional
@pytest.mark.parametrize(
    ("node_names", "expected_name"),
    [
        ((), "IndustrialPlant"),
        (("Sensors",), "Sensors"),
        (("Sensors", "Temperature"), "Temperature"),
        (("Sensors", "Pressure"), "Pressure"),
        (("Sensors", "Vibration"), "Vibration"),
        (("Motor",), "Motor"),
    ],
)
async def test_plant_nodes_are_browseable(
    opcua_client: OPCUATestClient,
    plant_path: Callable[..., list[str]],
    node_names: tuple[str, ...],
    expected_name: str,
) -> None:
    node = await opcua_client.get_node_by_path(plant_path(*node_names))

    assert (await node.read_browse_name()).Name == expected_name
