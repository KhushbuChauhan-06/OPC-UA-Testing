"""Development-only X.509 application-certificate generation using asyncua."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from cryptography.x509.oid import ExtendedKeyUsageOID

from asyncua.crypto.cert_gen import setup_self_signed_certificate


@dataclass(frozen=True)
class CertificateFiles:
    certificate: Path
    private_key: Path


async def generate_development_certificate_pair(directory: Path, name: str, application_uri: str) -> CertificateFiles:
    """Generate/reuse a self-signed development application certificate and private key."""
    directory.mkdir(parents=True, exist_ok=True)
    certificate = directory / f"{name}-cert.der"
    private_key = directory / f"{name}-key.pem"
    usages = [ExtendedKeyUsageOID.CLIENT_AUTH, ExtendedKeyUsageOID.SERVER_AUTH]
    await setup_self_signed_certificate(
        private_key,
        certificate,
        application_uri,
        "127.0.0.1",
        usages,
        {"commonName": name, "organizationName": "OPC UA Framework Development"},
    )
    return CertificateFiles(certificate=certificate, private_key=private_key)
