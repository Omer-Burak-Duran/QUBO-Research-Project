"""Gradient-statistics helpers for simple trainability studies."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np


@dataclass(slots=True)
class GradientSample:
    """One finite-difference gradient estimate."""

    sample_index: int
    objective_value: float
    gradient_norm: float
    max_abs_gradient: float
    parameter_vector: list[float]
    gradient_vector: list[float]

    def as_dict(self) -> dict[str, float | int | list[float]]:
        """Return a JSON-friendly representation."""
        return {
            "sample_index": self.sample_index,
            "objective_value": self.objective_value,
            "gradient_norm": self.gradient_norm,
            "max_abs_gradient": self.max_abs_gradient,
            "parameter_vector": list(self.parameter_vector),
            "gradient_vector": list(self.gradient_vector),
        }


def finite_difference_gradient(
    objective: Callable[[np.ndarray], float],
    parameters: np.ndarray,
    epsilon: float,
) -> np.ndarray:
    """Estimate a gradient with central finite differences."""
    if epsilon <= 0.0:
        msg = "Finite-difference epsilon must be positive."
        raise ValueError(msg)

    parameter_vector = np.asarray(parameters, dtype=float)
    gradient = np.zeros_like(parameter_vector, dtype=float)
    for index in range(parameter_vector.size):
        direction = np.zeros_like(parameter_vector, dtype=float)
        direction[index] = epsilon
        forward_value = objective(parameter_vector + direction)
        backward_value = objective(parameter_vector - direction)
        gradient[index] = (forward_value - backward_value) / (2.0 * epsilon)
    return gradient


def sample_gradient_statistics(
    *,
    objective: Callable[[np.ndarray], float],
    parameter_samples: list[np.ndarray],
    epsilon: float,
) -> list[GradientSample]:
    """Estimate gradient statistics over a collection of parameter samples."""
    samples: list[GradientSample] = []
    for sample_index, parameters in enumerate(parameter_samples):
        parameter_vector = np.asarray(parameters, dtype=float)
        gradient = finite_difference_gradient(objective, parameter_vector, epsilon)
        samples.append(
            GradientSample(
                sample_index=sample_index,
                objective_value=float(objective(parameter_vector)),
                gradient_norm=float(np.linalg.norm(gradient)),
                max_abs_gradient=float(np.max(np.abs(gradient))),
                parameter_vector=parameter_vector.tolist(),
                gradient_vector=gradient.tolist(),
            )
        )
    return samples


def summarize_gradient_samples(
    samples: list[GradientSample],
) -> dict[str, float | int]:
    """Return compact summary statistics for a set of gradient estimates."""
    if not samples:
        msg = "Gradient samples must not be empty."
        raise ValueError(msg)

    gradient_norms = np.asarray([sample.gradient_norm for sample in samples], dtype=float)
    objective_values = np.asarray([sample.objective_value for sample in samples], dtype=float)
    max_abs_gradients = np.asarray([sample.max_abs_gradient for sample in samples], dtype=float)
    return {
        "num_samples": len(samples),
        "mean_gradient_norm": float(np.mean(gradient_norms)),
        "variance_gradient_norm": float(np.var(gradient_norms)),
        "max_gradient_norm": float(np.max(gradient_norms)),
        "min_gradient_norm": float(np.min(gradient_norms)),
        "mean_max_abs_gradient": float(np.mean(max_abs_gradients)),
        "mean_objective_value": float(np.mean(objective_values)),
    }
