"""Supported Basic256Sha256 SecureChannel mode tests."""

from __future__ import annotations

import pytest
from asyncua import ua

from opcua_framework.client import OPCUAClientError, OPCUATestClient
from opcua_framework.utils.certificates import CertificateFiles


@pytest.mark.security
@pytest.mark.parametrize("mode", [ua.MessageSecurityMode.Sign, ua.MessageSecurityMode.SignAndEncrypt])
async def test_supported_basic256sha256_modes_connect(
    secure_server: tuple, certificate_files: dict[str, CertificateFiles], mode: ua.MessageSecurityMode
) -> None:
    server, _, _ = secure_server
    files = certificate_files["trusted_client"]
    client = OPCUATestClient(server.endpoint)
    await client.configure_basic256sha256(files.certificate, files.private_key, certificate_files["server"].certificate, mode)
    try:
        await client.connect()
        assert client.is_connected()
    finally:
        await client.disconnect()


@pytest.mark.security
async def test_mismatched_expected_server_certificate_fails(
    secure_server: tuple, certificate_files: dict[str, CertificateFiles]
) -> None:
    server, _, _ = secure_server
    files = certificate_files["trusted_client"]
    client = OPCUATestClient(server.endpoint)
    await client.configure_basic256sha256(files.certificate, files.private_key, certificate_files["wrong_server"].certificate)

    with pytest.raises(OPCUAClientError, match="Unable to connect"):
        await client.connect()
