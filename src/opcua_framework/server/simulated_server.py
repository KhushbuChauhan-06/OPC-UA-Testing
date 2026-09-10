"""Local simulated industrial OPC UA server used by integration tests."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import math
from dataclasses import dataclass
from pathlib import Path

from asyncua import Server, ua
from asyncua.common.node import Node
from asyncua import crypto

from .security import ServerSecurityConfig, TrustedCredentialUserManager

LOGGER = logging.getLogger(__name__)

DEFAULT_ENDPOINT = "opc.tcp://127.0.0.1:4840/abb-test-server/"
NAMESPACE_URI = "urn:opcua-framework:simulated-industrial-plant"


@dataclass(frozen=True)
class PlantNodes:
    """References to the simulated plant nodes after address-space creation."""

    industrial_plant: Node
    sensors: Node
    temperature: Node
    pressure: Node
    vibration: Node
    motor: Node
    speed: Node
    current: Node
    status: Node
    control: Node
    start_motor: Node
    stop_motor: Node


class OPCUATestServer:
    """Asynchronous local OPC UA server representing a small industrial plant.

    This is a simulation for test automation only. It does not model ABB hardware
    or a real industrial process.
    """

    def __init__(
        self,
        endpoint: str = DEFAULT_ENDPOINT,
        simulation_interval_seconds: float = 0.2,
        security_config: ServerSecurityConfig | None = None,
    ) -> None:
        if simulation_interval_seconds <= 0:
            raise ValueError("simulation_interval_seconds must be greater than zero")

        self.endpoint = endpoint
        self.simulation_interval_seconds = simulation_interval_seconds
        self._server: Server | None = None
        self._namespace_index: int | None = None
        self._nodes: PlantNodes | None = None
        self._simulation_task: asyncio.Task[None] | None = None
        self._state_lock = asyncio.Lock()
        self._motor_running = False
        self._simulation_phase = 0.0
        self._security_config = security_config

    @property
    def namespace_index(self) -> int:
        """Return the registered namespace index once the server has started."""
        if self._namespace_index is None:
            raise RuntimeError("Server has not started")
        return self._namespace_index

    @property
    def nodes(self) -> PlantNodes:
        """Return the address-space nodes once the server has started."""
        if self._nodes is None:
            raise RuntimeError("Address space has not been created")
        return self._nodes

    async def start(self) -> None:
        """Create the address space, start the endpoint, and begin simulation."""
        if self._server is not None:
            raise RuntimeError("Server is already running")

        user_manager = None
        if self._security_config is not None:
            user_manager = TrustedCredentialUserManager(self._security_config)
            await user_manager.load_trust_list()
        server = Server(user_manager=user_manager)
        await server.init()
        server.set_endpoint(self.endpoint)
        if self._security_config is not None:
            await server.load_certificate(self._security_config.certificate_path)
            await server.load_private_key(self._security_config.private_key_path)
            server.set_security_policy([
                ua.SecurityPolicyType.Basic256Sha256_Sign,
                ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
            ])
        self._namespace_index = await server.register_namespace(NAMESPACE_URI)
        self._server = server

        LOGGER.info("Creating industrial plant address space")
        await self._create_address_space()
        await server.start()
        self._simulation_task = asyncio.create_task(
            self._simulate_process(), name="opcua-plant-simulation"
        )
        LOGGER.info("OPC UA server started at %s", self.endpoint)
        LOGGER.info("Registered OPC UA namespace %s at index %s", NAMESPACE_URI, self.namespace_index)

    async def stop(self) -> None:
        """Stop simulation and release the server endpoint cleanly."""
        if self._server is None:
            return

        LOGGER.info("Shutting down OPC UA server at %s", self.endpoint)
        if self._simulation_task is not None:
            self._simulation_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._simulation_task
            self._simulation_task = None

        await self._server.stop()
        self._server = None
        self._nodes = None
        self._namespace_index = None
        LOGGER.info("OPC UA server shut down cleanly")

    async def _create_address_space(self) -> None:
        objects = self._require_server().nodes.objects
        industrial_plant = await objects.add_object(
            self._node_id("IndustrialPlant"), self._browse_name("IndustrialPlant")
        )
        sensors = await industrial_plant.add_object(
            self._node_id("Sensors"), self._browse_name("Sensors")
        )
        temperature = await sensors.add_variable(
            self._node_id("Temperature"), self._browse_name("Temperature"), 42.5, ua.VariantType.Float
        )
        pressure = await sensors.add_variable(
            self._node_id("Pressure"), self._browse_name("Pressure"), 6.2, ua.VariantType.Float
        )
        vibration = await sensors.add_variable(
            self._node_id("Vibration"), self._browse_name("Vibration"), 0.08, ua.VariantType.Float
        )

        motor = await industrial_plant.add_object(self._node_id("Motor"), self._browse_name("Motor"))
        speed = await motor.add_variable(
            self._node_id("Speed"), self._browse_name("Speed"), 0, ua.VariantType.Int32
        )
        await speed.set_writable()
        current = await motor.add_variable(
            self._node_id("Current"), self._browse_name("Current"), 0.0, ua.VariantType.Float
        )
        status = await motor.add_variable(
            self._node_id("Status"), self._browse_name("Status"), "STOPPED", ua.VariantType.String
        )

        control = await industrial_plant.add_object(
            self._node_id("Control"), self._browse_name("Control")
        )
        start_motor = await control.add_method(
            self._node_id("StartMotor"), self._browse_name("StartMotor"), self._start_motor
        )
        stop_motor = await control.add_method(
            self._node_id("StopMotor"), self._browse_name("StopMotor"), self._stop_motor
        )

        self._nodes = PlantNodes(
            industrial_plant=industrial_plant,
            sensors=sensors,
            temperature=temperature,
            pressure=pressure,
            vibration=vibration,
            motor=motor,
            speed=speed,
            current=current,
            status=status,
            control=control,
            start_motor=start_motor,
            stop_motor=stop_motor,
        )

    async def _start_motor(self, _parent_node_id: ua.NodeId) -> list[ua.Variant]:
        async with self._state_lock:
            self._motor_running = True
            await self.nodes.status.write_value("RUNNING", ua.VariantType.String)
            await self.nodes.speed.write_value(1500, ua.VariantType.Int32)
            await self.nodes.current.write_value(15.0, ua.VariantType.Float)
        LOGGER.info("Motor started")
        return []

    async def _stop_motor(self, _parent_node_id: ua.NodeId) -> list[ua.Variant]:
        async with self._state_lock:
            self._motor_running = False
            await self.nodes.status.write_value("STOPPED", ua.VariantType.String)
            await self.nodes.speed.write_value(0, ua.VariantType.Int32)
            await self.nodes.current.write_value(0.0, ua.VariantType.Float)
        LOGGER.info("Motor stopped")
        return []

    async def _simulate_process(self) -> None:
        while True:
            await asyncio.sleep(self.simulation_interval_seconds)
            async with self._state_lock:
                self._simulation_phase += 0.25
                await self.nodes.temperature.write_value(
                    round(42.5 + 1.5 * math.sin(self._simulation_phase), 2), ua.VariantType.Float
                )
                await self.nodes.pressure.write_value(
                    round(6.2 + 0.3 * math.sin(self._simulation_phase / 2), 2), ua.VariantType.Float
                )
                await self.nodes.vibration.write_value(
                    round(0.08 + 0.02 * math.cos(self._simulation_phase), 3), ua.VariantType.Float
                )
                if self._motor_running:
                    speed = await self.nodes.speed.read_value()
                    await self.nodes.current.write_value(
                        round(float(speed) / 100, 2), ua.VariantType.Float
                    )

    def _node_id(self, identifier: str) -> ua.NodeId:
        return ua.NodeId(identifier, self.namespace_index)

    def _browse_name(self, name: str) -> ua.QualifiedName:
        return ua.QualifiedName(name, self.namespace_index)

    def _require_server(self) -> Server:
        if self._server is None:
            raise RuntimeError("Server has not started")
        return self._server


async def run_server() -> None:
    """Run the local server until interrupted from the command line."""
    server = OPCUATestServer()
    await server.start()
    try:
        await asyncio.Event().wait()
    finally:
        await server.stop()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        pass
