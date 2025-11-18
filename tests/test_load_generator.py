"""Tests for the async load generator helpers."""

from __future__ import annotations

import pytest

from k8s_ml_predictive_autoscaling.load_generator import payload_stream
from k8s_ml_predictive_autoscaling.synthetic import PatternConfig, generate_profile


@pytest.mark.asyncio
async def test_payload_stream_cycles_values() -> None:
    profile = generate_profile(PatternConfig(minutes=2, seed=1))
    stream = payload_stream(profile)
    first = await stream.__anext__()
    second = await stream.__anext__()
    third = await stream.__anext__()
    assert first != second  # profile changes
    assert third == first  # cycle restarts after exhausting profile
