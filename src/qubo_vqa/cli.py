"""Command-line entrypoint for running small reproducible experiments."""

from __future__ import annotations

import argparse

from qubo_vqa.experiments import (
    run_experiment_from_config,
    run_qaoa_initialization_comparison,
    run_quantum_backend_comparison,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the project CLI parser."""
    parser = argparse.ArgumentParser(description="QUBO/VQA research project CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run an experiment from a YAML config file.")
    run_parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    run_parser.add_argument(
        "--output-dir",
        default=None,
        help="Optional base output directory. Overrides the config output directory.",
    )

    compare_parser = subparsers.add_parser(
        "compare-initializations",
        help="Compare QAOA initialization strategies from a YAML config file.",
    )
    compare_parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    compare_parser.add_argument(
        "--output-dir",
        default=None,
        help="Optional base output directory. Overrides the config output directory.",
    )

    backend_parser = subparsers.add_parser(
        "compare-backends",
        help="Compare exact, shot-based, and noisy backends from a YAML config file.",
    )
    backend_parser.add_argument("--config", required=True, help="Path to the YAML config file.")
    backend_parser.add_argument(
        "--output-dir",
        default=None,
        help="Optional base output directory. Overrides the config output directory.",
    )
    return parser


def main() -> None:
    """Execute the requested CLI command."""
    parser = build_parser()
    arguments = parser.parse_args()

    if arguments.command == "run":
        run_directory = run_experiment_from_config(
            config_path=arguments.config,
            output_directory=arguments.output_dir,
        )
        print(f"Experiment outputs written to: {run_directory}")
        return

    if arguments.command == "compare-initializations":
        run_directory = run_qaoa_initialization_comparison(
            config_path=arguments.config,
            output_directory=arguments.output_dir,
        )
        print(f"Initialization comparison outputs written to: {run_directory}")
        return

    if arguments.command == "compare-backends":
        run_directory = run_quantum_backend_comparison(
            config_path=arguments.config,
            output_directory=arguments.output_dir,
        )
        print(f"Backend comparison outputs written to: {run_directory}")


if __name__ == "__main__":
    main()
