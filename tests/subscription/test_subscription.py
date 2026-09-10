"""Integration tests for OPC UA subscriptions and monitored items."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from time import monotonic

import pytest
from asyncua import ua
from asyncua.common.node import Node

from opcua_framework.client import OPCUATestClient
from opcua_framework.config.test_data import SETTINGS, TEST_VALUES
from opcua_framework.server import OPCUATestServer

LOGGER = logging.getLogger(__name__)
NOTIFICATION_TIMEOUT_SECONDS = SETTINGS["opcua"]["notification_timeout_seconds"]
PUBLISHING_INTERVAL_MS = SETTINGS["opcua"]["subscription_publishing_interval_ms"]


@dataclass
class DataChangeCollector:
    """Collect data-change callbacks and expose event-driven waits for tests."""

    notifications: list[tuple[str, object]] = field(default_factory=list)
    event: asyncio.Event = field(default_factory=asyncio.Event)

    def datachange_notification(self, node: Node, value: object, _data: object) -> None:
        node_id = node.nodeid.to_string()
        self.notifications.append((node_id, value))
        LOGGER.info("Received data change for %s: %r", node_id, value)
        self.event.set()

    async def wait_for_value(self, node: Node, expected_value: object) -> None:
        """Wait only until a notification with the requested node and value arrives."""
        deadline = monotonic() + NOTIFICATION_TIMEOUT_SECONDS
        target_node_id = node.nodeid.to_string()
        while True:
            if (target_node_id, expected_value) in self.notifications:
                return

            self.event.clear()
            remaining = deadline - monotonic()
            if remaining <= 0:
                raise TimeoutError(f"No notification received for {target_node_id}")
            await asyncio.wait_for(self.event.wait(), timeout=remaining)

    async def wait_for_initial_notification(self) -> None:
        """Wait for the initial monitored-item value published by the server."""
        if self.notifications:
            return
        await asyncio.wait_for(self.event.wait(), timeout=NOTIFICATION_TIMEOUT_SECONDS)


@pytest.mark.subscription
async def test_subscription_creation_succeeds(opcua_client: OPCUATestClient) -> None:
    subscription = await opcua_client.create_subscription(PUBLISHING_INTERVAL_MS, DataChangeCollector())
    try:
        assert subscription.subscription_id is not None
    finally:
        await opcua_client.unsubscribe(subscription)


@pytest.mark.subscription
async def test_monitored_item_creation_succeeds(
    opcua_client: OPCUATestClient, plant_path: Callable[..., list[str]]
) -> None:
    speed = await opcua_client.get_node_by_path(plant_path("Motor", "Speed"))
    subscription = await opcua_client.create_subscription(PUBLISHING_INTERVAL_MS, DataChangeCollector())
    try:
        handle = await opcua_client.subscribe_to_data_change(subscription, speed)
        assert isinstance(handle, int)

        await opcua_client.unsubscribe(subscription, handle)
    finally:
        await opcua_client.unsubscribe(subscription)


@pytest.mark.subscription
async def test_temperature_change_generates_notification(
    opcua_client: OPCUATestClient,
    opcua_server: OPCUATestServer,
    plant_path: Callable[..., list[str]],
) -> None:
    temperature = await opcua_client.get_node_by_path(plant_path("Sensors", "Temperature"))
    collector = DataChangeCollector()
    subscription = await opcua_client.create_subscription(PUBLISHING_INTERVAL_MS, collector)
    try:
        await opcua_client.subscribe_to_data_change(subscription, temperature)
        await opcua_server.nodes.temperature.write_value(43.75, ua.VariantType.Float)

        await collector.wait_for_value(temperature, 43.75)
    finally:
        await opcua_client.unsubscribe(subscription)


@pytest.mark.subscription
async def test_motor_speed_change_generates_notification(
    opcua_client: OPCUATestClient, plant_path: Callable[..., list[str]]
) -> None:
    speed = await opcua_client.get_node_by_path(plant_path("Motor", "Speed"))
    collector = DataChangeCollector()
    subscription = await opcua_client.create_subscription(PUBLISHING_INTERVAL_MS, collector)
    try:
        await opcua_client.subscribe_to_data_change(subscription, speed)
        await opcua_client.write_value(speed, TEST_VALUES["subscription_motor_speed"], ua.VariantType.Int32)

        await collector.wait_for_value(speed, TEST_VALUES["subscription_motor_speed"])
    finally:
        await opcua_client.unsubscribe(subscription)


@pytest.mark.subscription
async def test_subscription_cleanup_succeeds(
    opcua_client: OPCUATestClient, plant_path: Callable[..., list[str]]
) -> None:
    pressure = await opcua_client.get_node_by_path(plant_path("Sensors", "Pressure"))
    subscription = await opcua_client.create_subscription(PUBLISHING_INTERVAL_MS, DataChangeCollector())
    await opcua_client.subscribe_to_data_change(subscription, pressure)

    await opcua_client.unsubscribe(subscription)

    assert opcua_client.is_connected()


@pytest.mark.subscription
async def test_timeout_is_bounded_when_speed_does_not_change(
    opcua_client: OPCUATestClient, plant_path: Callable[..., list[str]]
) -> None:
    speed = await opcua_client.get_node_by_path(plant_path("Motor", "Speed"))
    collector = DataChangeCollector()
    subscription = await opcua_client.create_subscription(PUBLISHING_INTERVAL_MS, collector)
    try:
        await opcua_client.subscribe_to_data_change(subscription, speed)
        await collector.wait_for_initial_notification()
        collector.event.clear()

        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(collector.event.wait(), timeout=SETTINGS["opcua"]["no_notification_timeout_seconds"])
    finally:
        await opcua_client.unsubscribe(subscription)
