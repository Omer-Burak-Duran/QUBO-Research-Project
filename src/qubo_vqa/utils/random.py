"""Reproducibility helpers for seeds and random generators."""

from __future__ import annotations

import random

import numpy as np


def set_global_seed(seed: int) -> np.random.Generator:
    """Seed Python and NumPy random state and return a fresh generator."""
    random.seed(seed)
    np.random.seed(seed)
    return np.random.default_rng(seed)
