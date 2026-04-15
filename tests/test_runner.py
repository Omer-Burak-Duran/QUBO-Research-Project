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


def test_runner_supports_minimum_vertex_cover_without_maxcut_plot(
    mvc_config_path,
    tmp_path,
) -> None:
    """The MVC starter experiment should save standard artifacts without a MaxCut plot."""
    run_directory = run_experiment_from_config(mvc_config_path, output_directory=tmp_path)

    assert (run_directory / "config.json").exists()
    assert (run_directory / "metrics.json").exists()
    assert (run_directory / "result.json").exists()
    assert (run_directory / "run_metadata.json").exists()
    assert (run_directory / "trace.json").exists()
    assert (run_directory / "artifacts" / "qubo_model.json").exists()
    assert (run_directory / "plots" / "energy_trace.png").exists()
    assert not (run_directory / "plots" / "maxcut_partition.png").exists()


def test_runner_supports_vqe_and_writes_ising_artifact(vqe_config_path, tmp_path) -> None:
    """The VQE starter experiment should save the standard quantum artifacts."""
    run_directory = run_experiment_from_config(vqe_config_path, output_directory=tmp_path)

    assert (run_directory / "config.json").exists()
    assert (run_directory / "metrics.json").exists()
    assert (run_directory / "result.json").exists()
    assert (run_directory / "run_metadata.json").exists()
    assert (run_directory / "trace.json").exists()
    assert (run_directory / "artifacts" / "qubo_model.json").exists()
    assert (run_directory / "artifacts" / "ising_model.json").exists()
    assert (run_directory / "plots" / "energy_trace.png").exists()
    assert (run_directory / "plots" / "maxcut_partition.png").exists()


def test_runner_supports_shot_based_qaoa_and_writes_ising_artifact(
    qaoa_shot_based_config_path,
    tmp_path,
) -> None:
    """The shot-based QAOA example should save the standard quantum artifacts."""
    run_directory = run_experiment_from_config(
        qaoa_shot_based_config_path,
        output_directory=tmp_path,
    )

    assert (run_directory / "config.json").exists()
    assert (run_directory / "metrics.json").exists()
    assert (run_directory / "result.json").exists()
    assert (run_directory / "run_metadata.json").exists()
    assert (run_directory / "trace.json").exists()
    assert (run_directory / "artifacts" / "qubo_model.json").exists()
    assert (run_directory / "artifacts" / "ising_model.json").exists()
    assert (run_directory / "plots" / "energy_trace.png").exists()
    assert (run_directory / "plots" / "maxcut_partition.png").exists()


def test_runner_supports_shot_based_vqe_and_writes_ising_artifact(
    vqe_shot_based_config_path,
    tmp_path,
) -> None:
    """The shot-based VQE example should save the standard quantum artifacts."""
    run_directory = run_experiment_from_config(
        vqe_shot_based_config_path,
        output_directory=tmp_path,
    )

    assert (run_directory / "config.json").exists()
    assert (run_directory / "metrics.json").exists()
    assert (run_directory / "result.json").exists()
    assert (run_directory / "run_metadata.json").exists()
    assert (run_directory / "trace.json").exists()
    assert (run_directory / "artifacts" / "qubo_model.json").exists()
    assert (run_directory / "artifacts" / "ising_model.json").exists()
    assert (run_directory / "plots" / "energy_trace.png").exists()
    assert (run_directory / "plots" / "maxcut_partition.png").exists()


def test_runner_supports_noisy_qaoa_and_writes_ising_artifact(
    qaoa_noisy_config_path,
    tmp_path,
) -> None:
    """The noisy QAOA example should save the standard quantum artifacts."""
    run_directory = run_experiment_from_config(
        qaoa_noisy_config_path,
        output_directory=tmp_path,
    )

    assert (run_directory / "config.json").exists()
    assert (run_directory / "metrics.json").exists()
    assert (run_directory / "result.json").exists()
    assert (run_directory / "run_metadata.json").exists()
    assert (run_directory / "trace.json").exists()
    assert (run_directory / "artifacts" / "qubo_model.json").exists()
    assert (run_directory / "artifacts" / "ising_model.json").exists()
    assert (run_directory / "plots" / "energy_trace.png").exists()
    assert (run_directory / "plots" / "maxcut_partition.png").exists()


def test_runner_supports_noisy_vqe_and_writes_ising_artifact(
    vqe_noisy_config_path,
    tmp_path,
) -> None:
    """The noisy VQE example should save the standard quantum artifacts."""
    run_directory = run_experiment_from_config(
        vqe_noisy_config_path,
        output_directory=tmp_path,
    )

    assert (run_directory / "config.json").exists()
    assert (run_directory / "metrics.json").exists()
    assert (run_directory / "result.json").exists()
    assert (run_directory / "run_metadata.json").exists()
    assert (run_directory / "trace.json").exists()
    assert (run_directory / "artifacts" / "qubo_model.json").exists()
    assert (run_directory / "artifacts" / "ising_model.json").exists()
    assert (run_directory / "plots" / "energy_trace.png").exists()
    assert (run_directory / "plots" / "maxcut_partition.png").exists()


def test_runner_supports_qaoa_mvc_without_maxcut_plot(
    qaoa_mvc_config_path,
    tmp_path,
) -> None:
    """The QAOA MVC example should save quantum artifacts without MaxCut plotting."""
    run_directory = run_experiment_from_config(qaoa_mvc_config_path, output_directory=tmp_path)

    assert (run_directory / "config.json").exists()
    assert (run_directory / "metrics.json").exists()
    assert (run_directory / "result.json").exists()
    assert (run_directory / "run_metadata.json").exists()
    assert (run_directory / "trace.json").exists()
    assert (run_directory / "artifacts" / "qubo_model.json").exists()
    assert (run_directory / "artifacts" / "ising_model.json").exists()
    assert (run_directory / "plots" / "energy_trace.png").exists()
    assert not (run_directory / "plots" / "maxcut_partition.png").exists()


def test_runner_supports_vqe_mvc_without_maxcut_plot(
    vqe_mvc_config_path,
    tmp_path,
) -> None:
    """The VQE MVC example should save quantum artifacts without MaxCut plotting."""
    run_directory = run_experiment_from_config(vqe_mvc_config_path, output_directory=tmp_path)

    assert (run_directory / "config.json").exists()
    assert (run_directory / "metrics.json").exists()
    assert (run_directory / "result.json").exists()
    assert (run_directory / "run_metadata.json").exists()
    assert (run_directory / "trace.json").exists()
    assert (run_directory / "artifacts" / "qubo_model.json").exists()
    assert (run_directory / "artifacts" / "ising_model.json").exists()
    assert (run_directory / "plots" / "energy_trace.png").exists()
    assert not (run_directory / "plots" / "maxcut_partition.png").exists()


def test_runner_supports_openjij_maxcut_without_ising_artifact(
    openjij_maxcut_config_path,
    tmp_path,
) -> None:
    """The OpenJij MaxCut example should save standard classical artifacts."""
    run_directory = run_experiment_from_config(
        openjij_maxcut_config_path,
        output_directory=tmp_path,
    )

    assert (run_directory / "config.json").exists()
    assert (run_directory / "metrics.json").exists()
    assert (run_directory / "result.json").exists()
    assert (run_directory / "run_metadata.json").exists()
    assert (run_directory / "trace.json").exists()
    assert (run_directory / "artifacts" / "qubo_model.json").exists()
    assert not (run_directory / "artifacts" / "ising_model.json").exists()
    assert (run_directory / "plots" / "energy_trace.png").exists()
    assert (run_directory / "plots" / "maxcut_partition.png").exists()
