"""Fixtures for real secure OPC UA integration tests."""

from __future__ import annotations

import secrets
from collections.abc import AsyncIterator
from pathlib import Path

import pytest_asyncio
from _pytest.monkeypatch import MonkeyPatch

from opcua_framework.server import OPCUATestServer, ServerSecurityConfig
from opcua_framework.utils.certificates import CertificateFiles, generate_development_certificate_pair


@pytest_asyncio.fixture
async def certificate_files(tmp_path: Path) -> dict[str, CertificateFiles]:
    return {
        "server": await generate_development_certificate_pair(tmp_path, "server", "urn:opcua-framework:server"),
        "trusted_client": await generate_development_certificate_pair(tmp_path, "trusted-client", "urn:opcua-framework:client:trusted"),
        "untrusted_client": await generate_development_certificate_pair(tmp_path, "untrusted-client", "urn:opcua-framework:client:untrusted"),
        "wrong_server": await generate_development_certificate_pair(tmp_path, "wrong-server", "urn:opcua-framework:server:wrong"),
    }


@pytest_asyncio.fixture
async def secure_server(
    certificate_files: dict[str, CertificateFiles], monkeypatch: MonkeyPatch
) -> AsyncIterator[tuple[OPCUATestServer, str, str]]:
    username = f"qa-{secrets.token_hex(8)}"
    password = secrets.token_urlsafe(24)
    monkeypatch.setenv("OPCUA_TEST_USERNAME", username)
    monkeypatch.setenv("OPCUA_TEST_PASSWORD", password)
    config = ServerSecurityConfig.from_environment(
        certificate_files["server"].certificate,
        certificate_files["server"].private_key,
        (certificate_files["trusted_client"].certificate,),
    )
    server = OPCUATestServer("opc.tcp://127.0.0.1:4841/abb-secure-test-server/", security_config=config)
    await server.start()
    try:
        yield server, username, password
    finally:
        await server.stop()
