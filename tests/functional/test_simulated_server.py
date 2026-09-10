"""Focused integration validation for the local simulated OPC UA server."""

from __future__ import annotations

import asyncio

import pytest
from asyncua import Client

from opcua_framework.server import NAMESPACE_URI, OPCUATestServer


@pytest.mark.functional
async def test_simulated_server_exposes_and_controls_industrial_plant() -> None:
    """Verify browsing, simulation, and motor methods through a real OPC UA connection."""
    server = OPCUATestServer(simulation_interval_seconds=0.05)
    await server.start()
    try:
        async with Client(url=server.endpoint) as client:
            namespace_index = await client.get_namespace_index(NAMESPACE_URI)
            objects = client.nodes.objects
            plant = await objects.get_child([f"{namespace_index}:IndustrialPlant"])
            temperature = await plant.get_child(
                [f"{namespace_index}:Sensors", f"{namespace_index}:Temperature"]
            )
            motor = await plant.get_child([f"{namespace_index}:Motor"])
            status = await motor.get_child([f"{namespace_index}:Status"])
            speed = await motor.get_child([f"{namespace_index}:Speed"])
            control = await plant.get_child([f"{namespace_index}:Control"])

            initial_temperature = await temperature.read_value()
            await asyncio.sleep(0.12)
            assert await temperature.read_value() != initial_temperature

            await control.call_method(f"{namespace_index}:StartMotor")
            assert await status.read_value() == "RUNNING"
            assert await speed.read_value() > 0

            await control.call_method(f"{namespace_index}:StopMotor")
            assert await status.read_value() == "STOPPED"
            assert await speed.read_value() == 0
    finally:
        await server.stop()
