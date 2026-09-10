"""Command-line entry point for the simulated OPC UA server."""

from __future__ import annotations

import asyncio
import logging

from .simulated_server import run_server


def main() -> None:
    """Start the simulated server until the user interrupts it."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
