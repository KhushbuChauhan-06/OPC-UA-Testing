"""Security configuration and authentication helpers for the simulated server."""

from __future__ import annotations

import hmac
import os
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from asyncua.server.user_managers import User, UserManager, UserRole
from asyncua.crypto import uacrypto

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ServerSecurityConfig:
    """Certificate, trust, and username authentication settings for one server."""

    certificate_path: Path
    private_key_path: Path
    trusted_client_certificates: tuple[Path, ...]
    username: str
    password: str

    @classmethod
    def from_environment(
        cls, certificate_path: Path, private_key_path: Path, trusted_clients: tuple[Path, ...]
    ) -> "ServerSecurityConfig":
        username = os.environ.get("OPCUA_TEST_USERNAME")
        password = os.environ.get("OPCUA_TEST_PASSWORD")
        if not username or not password:
            raise ValueError("OPCUA_TEST_USERNAME and OPCUA_TEST_PASSWORD must be set")
        return cls(certificate_path, private_key_path, trusted_clients, username, password)


class TrustedCredentialUserManager(UserManager):
    """Accept only a trusted SecureChannel client certificate and valid credentials."""

    def __init__(self, config: ServerSecurityConfig) -> None:
        self._username = config.username
        self._password = config.password
        self._trusted_certificates: set[bytes] = set()
        self._trusted_paths = config.trusted_client_certificates

    async def load_trust_list(self) -> None:
        for certificate_path in self._trusted_paths:
            certificate = await uacrypto.load_certificate(certificate_path)
            self._trusted_certificates.add(uacrypto.der_from_x509(certificate))
        LOGGER.info("Loaded %d trusted OPC UA client certificate(s)", len(self._trusted_certificates))

    def get_user(
        self,
        _iserver: Any,
        username: str | None = None,
        password: str | None = None,
        certificate: bytes | None = None,
    ) -> User | None:
        if certificate not in self._trusted_certificates:
            LOGGER.warning("Rejected session activation from an untrusted client certificate")
            return None
        if username is None and password is None:
            LOGGER.info("Authenticated trusted certificate client")
            return User(role=UserRole.User, name="trusted-certificate-client")
        if username == self._username and password is not None and hmac.compare_digest(password, self._password):
            LOGGER.info("Authenticated username client %s", username)
            return User(role=UserRole.User, name=username)
        LOGGER.warning("Rejected invalid username/password authentication")
        return None
