"""Reusable async OPC UA client wrapper for framework tests."""

from __future__ import annotations

import logging
from typing import Any, Sequence, TypeAlias

from asyncua import Client, ua
from asyncua.common.node import Node
from asyncua.common.subscription import Subscription
from asyncua.crypto.security_policies import SecurityPolicyBasic256Sha256

LOGGER = logging.getLogger(__name__)

NodeReference: TypeAlias = Node | ua.NodeId | str | int


class OPCUAClientError(RuntimeError):
    """Raised when a client-wrapper operation cannot be completed."""


class OPCUATestClient:
    """Small async wrapper that centralizes OPC UA session management.

    Security configuration is intentionally out of scope for this phase.
    """

    def __init__(self, endpoint: str, timeout_seconds: float = 4.0) -> None:
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds
        self._client: Client | None = None
        self._connected = False
        self._subscriptions: list[Subscription] = []

    async def configure_basic256sha256(
        self,
        certificate: str,
        private_key: str,
        server_certificate: str,
        mode: ua.MessageSecurityMode = ua.MessageSecurityMode.SignAndEncrypt,
    ) -> None:
        """Configure a Basic256Sha256 SecureChannel before connecting."""
        if self._client is not None:
            raise OPCUAClientError("Security must be configured before connecting")
        client = Client(url=self.endpoint, timeout=self.timeout_seconds)
        await client.set_security(
            SecurityPolicyBasic256Sha256,
            certificate,
            private_key,
            server_certificate=server_certificate,
            mode=mode,
        )
        self._client = client

    def set_credentials(self, username: str, password: str) -> None:
        """Set username credentials before connecting; values are not retained by the wrapper."""
        if self._client is None:
            self._client = Client(url=self.endpoint, timeout=self.timeout_seconds)
        if self._connected:
            raise OPCUAClientError("Credentials must be configured before connecting")
        self._client.set_user(username)
        self._client.set_password(password)

    async def connect(self) -> None:
        """Open an OPC UA connection and create an application session."""
        if self._connected:
            return

        if self._client is None:
            self._client = Client(url=self.endpoint, timeout=self.timeout_seconds)
        try:
            await self._client.connect()
        except Exception as exc:
            LOGGER.exception("Unable to connect to OPC UA endpoint %s", self.endpoint)
            await self.disconnect()
            raise OPCUAClientError(f"Unable to connect to OPC UA endpoint: {self.endpoint}") from exc

        self._connected = True
        LOGGER.info("Connected to OPC UA endpoint %s", self.endpoint)

    async def disconnect(self) -> None:
        """Delete active subscriptions and close the OPC UA session and connection."""
        client = self._client
        self._connected = False
        self._client = None

        try:
            for subscription in self._subscriptions:
                try:
                    await subscription.delete()
                except Exception:
                    LOGGER.warning("Unable to delete OPC UA subscription during cleanup", exc_info=True)
            self._subscriptions.clear()

            if client is not None:
                await client.disconnect()
                LOGGER.info("Disconnected from OPC UA endpoint %s", self.endpoint)
        except Exception:
            LOGGER.warning("An error occurred while disconnecting from %s", self.endpoint, exc_info=True)

    def is_connected(self) -> bool:
        """Return the wrapper's connection state."""
        return self._connected

    async def browse(self, node: NodeReference | None = None) -> list[Node]:
        """Return direct hierarchical children of a node, or of Objects by default."""
        try:
            target = self._require_client().nodes.objects if node is None else self.get_node(node)
            children = await target.get_children()
            LOGGER.info("Browsed OPC UA node %s; found %d children", target.nodeid, len(children))
            return children
        except OPCUAClientError:
            raise
        except Exception as exc:
            LOGGER.exception("Unable to browse OPC UA node")
            raise OPCUAClientError("Unable to browse OPC UA node") from exc

    def get_node(self, node: NodeReference) -> Node:
        """Resolve a NodeId or node reference through the active client."""
        try:
            if isinstance(node, Node):
                return node
            return self._require_client().get_node(node)
        except OPCUAClientError:
            raise
        except Exception as exc:
            LOGGER.exception("Unable to resolve OPC UA node %s", node)
            raise OPCUAClientError(f"Unable to resolve OPC UA node: {node}") from exc

    async def get_node_by_path(
        self, path: Sequence[str], start_node: NodeReference | None = None
    ) -> Node:
        """Resolve a browse path from Objects or a supplied starting node."""
        if not path:
            raise ValueError("path must contain at least one browse name")

        try:
            start = self._require_client().nodes.objects
            if start_node is not None:
                start = self.get_node(start_node)
            node = await start.get_child(list(path))
            LOGGER.info("Discovered OPC UA node at path %s", path)
            return node
        except OPCUAClientError:
            raise
        except Exception as exc:
            LOGGER.exception("Unable to resolve OPC UA browse path %s", path)
            raise OPCUAClientError(f"Unable to resolve OPC UA browse path: {path}") from exc

    async def read_value(self, node: NodeReference) -> Any:
        """Read and return a variable's value."""
        try:
            value = await self.get_node(node).read_value()
            LOGGER.info("Read OPC UA value from %s", self.get_node(node).nodeid)
            return value
        except OPCUAClientError:
            raise
        except Exception as exc:
            LOGGER.exception("Unable to read OPC UA value")
            raise OPCUAClientError("Unable to read OPC UA value") from exc

    async def write_value(
        self, node: NodeReference, value: Any, variant_type: ua.VariantType | None = None
    ) -> None:
        """Write a typed value to a writable OPC UA variable."""
        try:
            await self.get_node(node).write_value(value, variant_type)
            LOGGER.info("Wrote OPC UA value to %s", self.get_node(node).nodeid)
        except OPCUAClientError:
            raise
        except Exception as exc:
            LOGGER.exception("Unable to write OPC UA value")
            raise OPCUAClientError("Unable to write OPC UA value") from exc

    async def call_method(
        self, object_node: NodeReference, method: NodeReference, *arguments: Any
    ) -> Any:
        """Call a method exposed by an OPC UA object node."""
        try:
            method_id = self.get_node(method).nodeid
            result = await self.get_node(object_node).call_method(method_id, *arguments)
            LOGGER.info("Called OPC UA method %s on %s", method_id, self.get_node(object_node).nodeid)
            return result
        except OPCUAClientError:
            raise
        except Exception as exc:
            LOGGER.exception("Unable to call OPC UA method")
            raise OPCUAClientError("Unable to call OPC UA method") from exc

    async def create_subscription(self, period_ms: float, handler: Any) -> Subscription:
        """Create and retain an OPC UA subscription for later cleanup."""
        try:
            subscription = await self._require_client().create_subscription(period_ms, handler)
            self._subscriptions.append(subscription)
            LOGGER.info("Created OPC UA subscription with %.0f ms publishing interval", period_ms)
            return subscription
        except OPCUAClientError:
            raise
        except Exception as exc:
            LOGGER.exception("Unable to create OPC UA subscription")
            raise OPCUAClientError("Unable to create OPC UA subscription") from exc

    async def subscribe_to_data_change(
        self, subscription: Subscription, node: NodeReference
    ) -> int:
        """Subscribe to data changes for one variable and return its handle."""
        try:
            return await subscription.subscribe_data_change(self.get_node(node))
        except OPCUAClientError:
            raise
        except Exception as exc:
            LOGGER.exception("Unable to subscribe to OPC UA data changes")
            raise OPCUAClientError("Unable to subscribe to OPC UA data changes") from exc

    async def unsubscribe(self, subscription: Subscription, handle: int | None = None) -> None:
        """Remove one monitored item, or delete the complete subscription."""
        try:
            if handle is None:
                await subscription.delete()
                if subscription in self._subscriptions:
                    self._subscriptions.remove(subscription)
            else:
                await subscription.unsubscribe(handle)
        except Exception as exc:
            LOGGER.exception("Unable to unsubscribe from OPC UA data changes")
            raise OPCUAClientError("Unable to unsubscribe from OPC UA data changes") from exc

    def _require_client(self) -> Client:
        if self._client is None or not self._connected:
            raise OPCUAClientError("OPC UA client is not connected")
        return self._client
