"""Timing helpers for lightweight experiment instrumentation."""

from __future__ import annotations

from contextlib import contextmanager
from time import perf_counter


@contextmanager
def timed_block() -> float:
    """Yield a closure that reports elapsed wall-clock seconds."""
    started_at = perf_counter()

    def elapsed_seconds() -> float:
        return perf_counter() - started_at

    yield elapsed_seconds
