# How To Run

This guide explains how to install, test, and run the completed QUBO/VQA project from the repository root.

The commands below match the current repository layout, CLI, and configs in `configs/experiments/`. They were checked against the actual project entrypoint `python -m qubo_vqa.cli`.

## What This Project Runs

The current implemented benchmark scope is:

- `MaxCut`
- `Minimum Vertex Cover`
- classical baselines with `brute_force` and `openjij`
- variational solvers with `qaoa` and `vqe`
- backend modes `statevector`, `shot_based`, and `noisy`
- comparison workflows for solvers, QAOA initialization, and backends
- benchmark campaigns and landscape analysis

## Prerequisites

- Windows PowerShell commands below assume you are in the repository root.
- Python `3.12.x` is required by `pyproject.toml`.
- For the full project workflow, install the project with the `dev`, `classical`, and `quantum` extras.

Optional dependency groups:

- `.[dev]`: tests and linting only
- `.[dev,classical]`: adds `openjij` and `pulp`
- `.[dev,classical,quantum]`: full repository workflow, including Qiskit and Aer

## Environment Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
& ".\.venv\Scripts\Activate.ps1"
```

Install the full environment:

```powershell
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -e .[dev,classical,quantum]
```

You can also install from `requirements.txt`, which currently points at the same full editable environment:

```powershell
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
```

## Main CLI

The project is designed to be run from:

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli <subcommand> --config <yaml>
```

Available subcommands:

- `run`
- `compare-solvers`
- `compare-backends`
- `compare-initializations`
- `analyze-landscape`
- `run-benchmark-campaign`

You can optionally override the output root with:

```powershell
--output-dir data/results/<your-folder>
```

## Run Tests

Run the full test suite:

```powershell
& ".\.venv\Scripts\python.exe" -m pytest
```

Expected current baseline: `44 passed`.

## Starter Single Runs

### Classical MaxCut

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/classical_maxcut.yaml
```

### Classical Minimum Vertex Cover

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/classical_min_vertex_cover.yaml
```

### QAOA MaxCut

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/qaoa_maxcut_statevector.yaml
```

### VQE MaxCut

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/vqe_maxcut_statevector.yaml
```

### QAOA Minimum Vertex Cover

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/qaoa_min_vertex_cover_statevector.yaml
```

### VQE Minimum Vertex Cover

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/vqe_min_vertex_cover_statevector.yaml
```

## Comparison And Analysis Workflows

### Solver Comparison

Compares `brute_force`, `openjij`, `qaoa`, and `vqe` on the same MaxCut instance.

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli compare-solvers --config configs/experiments/maxcut_solver_comparison.yaml
```

### QAOA Backend Comparison

Compares `statevector`, `shot_based`, and `noisy` QAOA runs on the same MaxCut instance.

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli compare-backends --config configs/experiments/qaoa_backend_comparison.yaml
```

### QAOA Initialization Comparison

Compares `interpolation`, `warm_start`, and `random` initialization strategies over QAOA depths.

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli compare-initializations --config configs/experiments/qaoa_initialization_comparison.yaml
```

### Landscape Analysis

Runs the preserved Milestone 12 workflow:

- QAOA `p=1` landscape heatmap
- QAOA multi-start convergence
- QAOA gradient statistics
- VQE gradient statistics

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli analyze-landscape --config configs/experiments/qaoa_landscape_analysis.yaml
```

## Benchmark Campaigns

### Starter Campaign

Smallest complete aggregate benchmark slice.

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run-benchmark-campaign --config configs/experiments/starter_benchmark_campaign.yaml
```

### Moderate Campaign

Broader statevector-only benchmark slice over 4-node and 6-node instances.

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run-benchmark-campaign --config configs/experiments/moderate_benchmark_campaign.yaml
```

### Backend-Focused Campaign

Adds `shot_based` and `noisy` backend comparisons across shared small MaxCut and MVC instances.

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run-benchmark-campaign --config configs/experiments/backend_benchmark_campaign.yaml
```

## What The Main Configs Do

### Single-run configs

Files such as:

- `configs/experiments/classical_maxcut.yaml`
- `configs/experiments/classical_min_vertex_cover.yaml`
- `configs/experiments/qaoa_maxcut_statevector.yaml`
- `configs/experiments/vqe_maxcut_statevector.yaml`
- `configs/experiments/qaoa_min_vertex_cover_statevector.yaml`
- `configs/experiments/vqe_min_vertex_cover_statevector.yaml`

These define:

- one problem instance
- one solver
- solver parameters
- output tag

### Comparison configs

- `configs/experiments/maxcut_solver_comparison.yaml`
- `configs/experiments/qaoa_backend_comparison.yaml`
- `configs/experiments/qaoa_initialization_comparison.yaml`
- `configs/experiments/qaoa_landscape_analysis.yaml`

These define one shared problem instance and then compare:

- multiple solver families
- multiple backends
- multiple QAOA initialization strategies
- or landscape / gradient-analysis settings

### Campaign configs

- `configs/experiments/starter_benchmark_campaign.yaml`
- `configs/experiments/moderate_benchmark_campaign.yaml`
- `configs/experiments/backend_benchmark_campaign.yaml`

These define benchmark datasets using:

- explicit problem cases
- optional problem sweeps
- explicit solver cases
- optional solver sweeps
- exact-reference limits

## Where Outputs Are Saved

By default, configs write into:

```text
data/results/
```

Each run creates a timestamped folder:

```text
data/results/<tag>-YYYYMMDD-HHMMSS/
```

If you pass `--output-dir`, the timestamped run folder is created underneath that directory instead.

### Standard single-run artifacts

Single runs produce files such as:

- `config.json`
- `result.json`
- `metrics.json`
- `run_metadata.json`
- `trace.json`
- `artifacts/qubo_model.json`
- `artifacts/ising_model.json` for quantum runs
- `plots/energy_trace.png`
- `plots/maxcut_partition.png` for MaxCut runs

### Comparison outputs

Comparison workflows add:

- `summary.json`
- `tables/*.csv`
- `traces/*.json`
- aggregate comparison plots under `plots/`

### Benchmark campaign outputs

Campaigns add:

- nested per-run folders under `runs/`
- `summary.json`
- `notes.md`
- aggregate tables under `tables/`
- aggregate plots under `plots/`

## Reproduce The Main Runs Used For The Report

The report written in this repository was based on the following command set from the repo root:

```powershell
& ".\.venv\Scripts\python.exe" -m pytest
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/classical_maxcut.yaml --output-dir data/results/session-20260415
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/classical_min_vertex_cover.yaml --output-dir data/results/session-20260415
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/qaoa_maxcut_statevector.yaml --output-dir data/results/session-20260415
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/vqe_maxcut_statevector.yaml --output-dir data/results/session-20260415
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/qaoa_min_vertex_cover_statevector.yaml --output-dir data/results/session-20260415
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/vqe_min_vertex_cover_statevector.yaml --output-dir data/results/session-20260415
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli compare-solvers --config configs/experiments/maxcut_solver_comparison.yaml --output-dir data/results/session-20260415
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli compare-backends --config configs/experiments/qaoa_backend_comparison.yaml --output-dir data/results/session-20260415
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli compare-initializations --config configs/experiments/qaoa_initialization_comparison.yaml --output-dir data/results/session-20260415
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli analyze-landscape --config configs/experiments/qaoa_landscape_analysis.yaml --output-dir data/results/session-20260415
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run-benchmark-campaign --config configs/experiments/starter_benchmark_campaign.yaml --output-dir data/results/session-20260415
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run-benchmark-campaign --config configs/experiments/moderate_benchmark_campaign.yaml --output-dir data/results/session-20260415
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run-benchmark-campaign --config configs/experiments/backend_benchmark_campaign.yaml --output-dir data/results/session-20260415
```

This creates the report session outputs under:

```text
data/results/session-20260415/
```

## Practical Notes

- Use the virtualenv interpreter explicitly if you want the most reproducible behavior on Windows.
- `data/` is gitignored, so your run artifacts stay local unless you export or copy them elsewhere.
- For small benchmark instances, the repository frequently reaches the exact optimum even when optimizer success flags are mixed. Check both the objective/optimality metrics and the optimizer status fields.
- The broadest executed dataset in this repository is still moderate in scale. It is suitable for a course research report, not for publication-scale benchmarking claims.
