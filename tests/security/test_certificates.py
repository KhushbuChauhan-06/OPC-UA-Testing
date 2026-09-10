"""Certificate trust tests using real X.509 application certificates."""

from __future__ import annotations

import pytest

from opcua_framework.client import OPCUAClientError, OPCUATestClient
from opcua_framework.utils.certificates import CertificateFiles


@pytest.mark.security
async def test_trusted_client_certificate_connects(secure_server: tuple, certificate_files: dict[str, CertificateFiles]) -> None:
    server, _, _ = secure_server
    client = OPCUATestClient(server.endpoint)
    trusted = certificate_files["trusted_client"]
    await client.configure_basic256sha256(trusted.certificate, trusted.private_key, certificate_files["server"].certificate)
    try:
        await client.connect()
        assert client.is_connected()
    finally:
        await client.disconnect()


@pytest.mark.security
async def test_untrusted_client_certificate_is_rejected(secure_server: tuple, certificate_files: dict[str, CertificateFiles]) -> None:
    server, _, _ = secure_server
    client = OPCUATestClient(server.endpoint)
    untrusted = certificate_files["untrusted_client"]
    await client.configure_basic256sha256(untrusted.certificate, untrusted.private_key, certificate_files["server"].certificate)

    with pytest.raises(OPCUAClientError, match="Unable to connect"):
        await client.connect()
    assert not client.is_connected()
