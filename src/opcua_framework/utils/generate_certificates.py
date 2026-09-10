"""Generate ignored development certificates for manual secure-server runs."""

from __future__ import annotations

import asyncio
from pathlib import Path

from .certificates import generate_development_certificate_pair


async def main() -> None:
    directory = Path("certificates")
    await generate_development_certificate_pair(directory, "server", "urn:opcua-framework:server")
    await generate_development_certificate_pair(directory, "client", "urn:opcua-framework:client")
    print(f"Development certificates created in {directory.resolve()}")


if __name__ == "__main__":
    asyncio.run(main())
