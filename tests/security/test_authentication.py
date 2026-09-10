"""Username authentication tests over a real signed-and-encrypted SecureChannel."""

from __future__ import annotations

import pytest

from opcua_framework.client import OPCUAClientError, OPCUATestClient
from opcua_framework.utils.certificates import CertificateFiles


async def secure_client(endpoint: str, files: dict[str, CertificateFiles]) -> OPCUATestClient:
    client = OPCUATestClient(endpoint)
    trusted = files["trusted_client"]
    await client.configure_basic256sha256(trusted.certificate, trusted.private_key, files["server"].certificate)
    return client


@pytest.mark.security
async def test_valid_username_password_authenticates(
    secure_server: tuple, certificate_files: dict[str, CertificateFiles]
) -> None:
    server, username, password = secure_server
    client = await secure_client(server.endpoint, certificate_files)
    client.set_credentials(username, password)
    try:
        await client.connect()
        assert client.is_connected()
    finally:
        await client.disconnect()


@pytest.mark.security
@pytest.mark.parametrize("credential_kind", ["wrong_password", "unknown_user"])
async def test_invalid_username_credentials_are_rejected(
    secure_server: tuple, certificate_files: dict[str, CertificateFiles], credential_kind: str
) -> None:
    server, username, password = secure_server
    client = await secure_client(server.endpoint, certificate_files)
    client.set_credentials(username if credential_kind == "wrong_password" else f"unknown-{username}", password + "invalid")

    with pytest.raises(OPCUAClientError, match="Unable to connect"):
        await client.connect()
    assert not client.is_connected()
