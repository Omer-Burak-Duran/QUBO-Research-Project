"""Tests for the config-driven experiment runner."""

from __future__ import annotations

from qubo_vqa.experiments.runner import run_experiment_from_config


def test_runner_creates_standard_artifacts(sample_config_path, tmp_path) -> None:
    """The starter experiment should save config, metrics, result, and plots."""
    run_directory = run_experiment_from_config(sample_config_path, output_directory=tmp_path)

    assert (run_directory / "config.json").exists()
    assert (run_directory / "metrics.json").exists()
    assert (run_directory / "result.json").exists()
    assert (run_directory / "run_metadata.json").exists()
    assert (run_directory / "trace.json").exists()
    assert (run_directory / "artifacts" / "qubo_model.json").exists()
    assert (run_directory / "plots" / "energy_trace.png").exists()
    assert (run_directory / "plots" / "maxcut_partition.png").exists()
