"""Initialization helpers for QAOA parameter vectors."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


@dataclass(slots=True)
class QAOAInitializationConfig:
    """Configuration for selecting the initial QAOA parameter vector."""

    strategy: str = "random"
    seed: int | None = None
    gamma_bounds: tuple[float, float] = (0.0, math.pi)
    beta_bounds: tuple[float, float] = (0.0, math.pi / 2.0)

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-friendly representation."""
        return {
            "strategy": self.strategy,
            "seed": self.seed,
            "gamma_bounds": list(self.gamma_bounds),
            "beta_bounds": list(self.beta_bounds),
        }


SUPPORTED_QAOA_INITIALIZATIONS = ("random", "warm_start", "interpolation")


def initialize_qaoa_parameters(
    reps: int,
    config: QAOAInitializationConfig,
    previous_parameters: np.ndarray | None = None,
) -> np.ndarray:
    """Create an initial parameter vector in [gamma_0..gamma_p-1, beta_0..beta_p-1] order."""
    if reps <= 0:
        msg = "QAOA reps must be positive."
        raise ValueError(msg)

    if config.strategy == "random":
        rng = np.random.default_rng(config.seed)
        gammas = rng.uniform(config.gamma_bounds[0], config.gamma_bounds[1], size=reps)
        betas = rng.uniform(config.beta_bounds[0], config.beta_bounds[1], size=reps)
        return np.concatenate([gammas, betas]).astype(float)

    if config.strategy == "interpolation":
        gammas = np.linspace(0.15, 0.65, reps, dtype=float)
        betas = np.linspace(0.35, 0.10, reps, dtype=float)
        return np.concatenate([gammas, betas])

    if config.strategy == "warm_start":
        if previous_parameters is None:
            msg = "warm_start initialization requires previous_parameters."
            raise ValueError(msg)
        previous = np.asarray(previous_parameters, dtype=float)
        if previous.ndim != 1 or previous.size % 2 != 0:
            msg = "previous_parameters must be a flat vector with gamma and beta blocks."
            raise ValueError(msg)
        previous_reps = previous.size // 2
        if previous_reps >= reps:
            msg = "warm_start requires previous_parameters from a strictly smaller depth."
            raise ValueError(msg)
        previous_gammas = previous[:previous_reps]
        previous_betas = previous[previous_reps:]
        gammas = np.interp(
            np.linspace(0.0, 1.0, reps),
            np.linspace(0.0, 1.0, previous_reps),
            previous_gammas,
        )
        betas = np.interp(
            np.linspace(0.0, 1.0, reps),
            np.linspace(0.0, 1.0, previous_reps),
            previous_betas,
        )
        return np.concatenate([gammas, betas])

    msg = f"Unsupported QAOA initialization strategy '{config.strategy}'."
    raise NotImplementedError(msg)
