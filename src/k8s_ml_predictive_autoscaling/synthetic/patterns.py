"""Deterministic helpers to craft synthetic demand patterns."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(slots=True)
class PatternConfig:
    """Configuration bag for synthetic load generation."""

    minutes: int = 24 * 60
    baseline: float = 0.3
    daily_amplitude: float = 0.5
    weekly_drop: float = 0.4
    spike_probability: float = 0.03
    spike_intensity: float = 0.6
    seed: int | None = None


def generate_profile(config: PatternConfig | None = None) -> list[float]:
    """Generate a normalized load profile combining day/week cycles and spikes."""

    config = config or PatternConfig()
    rng = random.Random(config.seed)
    values: list[float] = []
    for minute in range(config.minutes):
        day_progress = (minute % (24 * 60)) / (24 * 60)
        weekday = (minute // (24 * 60)) % 7
        daily_component = math.sin(2 * math.pi * day_progress - math.pi / 2)
        daily_component = (daily_component + 1) / 2  # normalize 0..1
        weekly_modifier = 1 - config.weekly_drop if weekday < 5 else 1 - (config.weekly_drop * 1.5)
        value = config.baseline + config.daily_amplitude * daily_component * weekly_modifier
        if rng.random() < config.spike_probability:
            value += rng.random() * config.spike_intensity
        values.append(max(value, 0))
    return values


def windowed(values: Sequence[float], size: int) -> Iterable[list[float]]:
    """Yield sliding windows from the generated profile."""

    if size <= 0:
        raise ValueError("Window size must be positive")
    for index in range(0, len(values) - size + 1):
        yield list(values[index : index + size])


__all__ = ["PatternConfig", "generate_profile", "windowed"]
