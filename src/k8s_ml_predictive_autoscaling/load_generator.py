"""Async synthetic load generator for demo services."""

from __future__ import annotations

import argparse
import asyncio
import itertools
import json
import signal
from collections.abc import AsyncIterator

import httpx

from .logging import get_logger, log_structured
from .settings import get_settings
from .synthetic import PatternConfig, generate_profile

LOGGER = get_logger(__name__)


async def payload_stream(profile: list[float]) -> AsyncIterator[dict[str, float]]:
    """Yield payloads based on a deterministic profile.

    Args:
        profile: Normalized load profile values between 0 and 1.

    Yields:
        Request payloads with payload_size / cpu_hint fields.
    """

    for value in itertools.cycle(profile):
        yield {
            "payload_size": 64,
            "cpu_hint": 0.02 + value * 0.05,
        }


async def hit_targets(
    targets: list[str],
    interval: float,
    profile: list[float],
    stop_event: asyncio.Event,
) -> None:
    """Continuously POST synthetic workload payloads to given targets.

    Args:
        targets: Base URLs for demo services.
        interval: Delay between batches in seconds.
        profile: Normalized load profile.
        stop_event: Stop flag controlled by signal handlers.
    """

    async with httpx.AsyncClient(timeout=5.0) as client:
        async for body in payload_stream(profile):
            if stop_event.is_set():
                break
            for target in targets:
                try:
                    response = await client.post(f"{target}/workload", json=body)
                    log_structured(
                        LOGGER,
                        "sent synthetic payload",
                        target=target,
                        status=response.status_code,
                    )
                except httpx.HTTPError as exc:  # pragma: no cover - network dependent
                    LOGGER.warning("Load generator request failed: %s", exc)
            await asyncio.sleep(interval)


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser for the load generator."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--targets",
        nargs="+",
        required=True,
        help="List of service base URLs to hit (e.g. http://demo-service-a:8000)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Delay between batches in seconds",
    )
    parser.add_argument(
        "--minutes",
        type=int,
        default=60,
        help="Profile length in minutes",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for deterministic profile",
    )
    return parser


async def _run_async(targets: list[str], interval: float, minutes: int, seed: int) -> None:
    """Entry point wiring profile generation and async loop.

    Args:
        targets: List of service base URLs.
        interval: Delay between payload batches.
        minutes: Profile length before repeating.
        seed: RNG seed to keep experiments reproducible.
    """
    pattern = generate_profile(PatternConfig(minutes=minutes, seed=seed))
    stop_event = asyncio.Event()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    await hit_targets(targets, interval, pattern, stop_event)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    LOGGER.info(
        "Starting load generator",
        extra={"targets": args.targets},
    )
    asyncio.run(_run_async(args.targets, args.interval, args.minutes, args.seed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
