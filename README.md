# QUBO-Research-Project

Research-oriented Python codebase for:

- transparent QUBO modeling of benchmark combinatorial problems,
- classical and quantum solver comparisons on shared encodings,
- reproducible experiment execution and artifact saving,
- optimization-landscape analysis for QAOA and VQE.

## Current foundation

This repository currently implements the current stable foundation:

- canonical `QUBOModel`, `IsingModel`, and standardized result containers,
- QUBO-to-Ising conversion utilities,
- a complete `MaxCut` benchmark encoder and decoder,
- a complete `Minimum Vertex Cover` benchmark encoder and decoder,
- an exact brute-force classical baseline,
- an OpenJij classical sampling baseline,
- a config-driven experiment runner with saved JSON artifacts and plots,
- exact-statevector QAOA paths for small MaxCut and tiny MVC instances,
- exact-statevector VQE paths for small MaxCut and tiny MVC instances,
- a reproducible shot-based backend toggle for the current small quantum paths,
- Aer-backed noisy quantum paths for the current small MaxCut examples,
- a config-driven backend comparison workflow for exact vs shot-based vs noisy QAOA,
- a config-driven solver comparison workflow for brute force vs OpenJij vs QAOA vs VQE,
- config-driven benchmark campaigns with grouped aggregate tables and interpretation notes,
- a config-driven QAOA initialization comparison workflow,
- standard QAOA comparison tables and benchmark-style plots for the current MaxCut path,
- a first preserved landscape-analysis workflow for the current MaxCut path.

## Installation

```bash
pip install -e .[dev,classical,quantum]
```

If you only need the brute-force classical baseline path, `pip install -e .[dev]` is enough.
If you want the OpenJij baseline without the quantum stack, use `pip install -e .[dev,classical]`.

## Run the first example

```bash
python -m qubo_vqa.cli run --config configs/experiments/classical_maxcut.yaml
```

## Run the QAOA example

```bash
python -m qubo_vqa.cli run --config configs/experiments/qaoa_maxcut_statevector.yaml
```

## Run the VQE example

```bash
python -m qubo_vqa.cli run --config configs/experiments/vqe_maxcut_statevector.yaml
```

## Run the shot-based QAOA example

```bash
python -m qubo_vqa.cli run --config configs/experiments/qaoa_maxcut_shot_based.yaml
```

This finite-shot config reuses the same MaxCut starter instance and records the
backend mode, shot count, and backend seed in the standard result schema.

## Run the shot-based VQE example

```bash
python -m qubo_vqa.cli run --config configs/experiments/vqe_maxcut_shot_based.yaml
```

This uses the same finite-shot backend toggle for the current small VQE path.
It is currently a runnable starter config, while richer shot-based VQE tuning is
still deferred.

## Run the noisy QAOA example

```bash
python -m qubo_vqa.cli run --config configs/experiments/qaoa_maxcut_noisy.yaml
```

This uses an Aer-backed sampled noise model and records the backend mode, shot
count, noise model name, and seed in the standard result schema.

## Run the noisy VQE example

```bash
python -m qubo_vqa.cli run --config configs/experiments/vqe_maxcut_noisy.yaml
```

## Compare backend modes

```bash
python -m qubo_vqa.cli compare-backends --config configs/experiments/qaoa_backend_comparison.yaml
```

This comparison command benchmarks the current MaxCut QAOA path across
`statevector`, `shot_based`, and `noisy` execution, and saves grouped metrics,
CSV tables, per-run traces, and backend-comparison plots under `data/results/`.

## Run the OpenJij MaxCut example

```bash
python -m qubo_vqa.cli run --config configs/experiments/openjij_maxcut.yaml
```

## Run the OpenJij MVC example

```bash
python -m qubo_vqa.cli run --config configs/experiments/openjij_min_vertex_cover.yaml
```

These two configs preserve the new Milestone 13 OpenJij baseline on the current
starter MaxCut and Minimum Vertex Cover instances.

## Run the Minimum Vertex Cover example

```bash
python -m qubo_vqa.cli run --config configs/experiments/classical_min_vertex_cover.yaml
```

## Run the QAOA MVC example

```bash
python -m qubo_vqa.cli run --config configs/experiments/qaoa_min_vertex_cover_statevector.yaml
```

## Run the VQE MVC example

```bash
python -m qubo_vqa.cli run --config configs/experiments/vqe_min_vertex_cover_statevector.yaml
```

These two configs use the same tiny 4-node MVC cycle instance and emit the same
standardized result schema, so their `result.json` and `metrics.json` outputs can
be compared side by side with the existing QAOA/VQE MaxCut runs.

## Compare QAOA initialization strategies

```bash
python -m qubo_vqa.cli compare-initializations --config configs/experiments/qaoa_initialization_comparison.yaml
```

This comparison command benchmarks `interpolation`, `warm_start`, and `random`
initialization on the current MaxCut statevector path and saves grouped metrics,
CSV tables, per-run traces, and benchmark-style plots under `data/results/`.

## Compare solver families on MaxCut

```bash
python -m qubo_vqa.cli compare-solvers --config configs/experiments/maxcut_solver_comparison.yaml
```

This Milestone 13 workflow benchmarks the shared starter MaxCut instance across
`brute_force`, `openjij`, `qaoa`, and `vqe`, and saves grouped comparison
metrics, CSV tables, per-run traces, and solver-comparison plots.

## Run the starter benchmark campaign

```bash
python -m qubo_vqa.cli run-benchmark-campaign --config configs/experiments/starter_benchmark_campaign.yaml
```

This fast Milestone 14/15 smoke path benchmarks preserved MaxCut and Minimum
Vertex Cover starter cases across brute force, OpenJij, QAOA, and VQE variants.

## Run the moderate benchmark campaign

```bash
python -m qubo_vqa.cli run-benchmark-campaign --config configs/experiments/moderate_benchmark_campaign.yaml
```

This repository-level benchmark path expands the preserved campaign to multiple
problem sizes/families plus QAOA/VQE depth variants while keeping exact
references feasible.

## Run the backend-focused benchmark campaign

```bash
python -m qubo_vqa.cli run-benchmark-campaign --config configs/experiments/backend_benchmark_campaign.yaml
```

This campaign emphasizes exact vs shot-based vs noisy backend behavior across a
shared small MaxCut/MVC benchmark slice.

All benchmark-campaign runs save:

- nested per-run artifacts under `runs/`
- `tables/run_metrics.csv`
- grouped aggregate tables for cases, solver families, problem families, sizes,
  backends, and QAOA/VQE depth slices
- `summary.json`
- `notes.md`
- aggregate benchmark plots under `plots/`

## Run the first landscape-analysis example

```bash
python -m qubo_vqa.cli analyze-landscape --config configs/experiments/qaoa_landscape_analysis.yaml
```

This Milestone 12 workflow preserves one config-driven landscape path on the
starter MaxCut instance and saves:

- a QAOA `p=1` landscape heatmap,
- a multi-start QAOA convergence plot,
- QAOA and VQE finite-difference gradient-statistics tables and plots.

## Run the tests

```bash
pytest
```

The validated repository commands in this project have been run through the virtual environment interpreter:

```powershell
& ".\.venv\Scripts\python.exe" -m pytest
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/classical_maxcut.yaml
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/qaoa_maxcut_statevector.yaml
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/vqe_maxcut_statevector.yaml
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/qaoa_maxcut_shot_based.yaml
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/vqe_maxcut_shot_based.yaml
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/qaoa_maxcut_noisy.yaml
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/vqe_maxcut_noisy.yaml
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli compare-backends --config configs/experiments/qaoa_backend_comparison.yaml
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/openjij_maxcut.yaml
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/openjij_min_vertex_cover.yaml
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/classical_min_vertex_cover.yaml
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/qaoa_min_vertex_cover_statevector.yaml
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/vqe_min_vertex_cover_statevector.yaml
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli compare-initializations --config configs/experiments/qaoa_initialization_comparison.yaml
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli analyze-landscape --config configs/experiments/qaoa_landscape_analysis.yaml
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli compare-solvers --config configs/experiments/maxcut_solver_comparison.yaml
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run-benchmark-campaign --config configs/experiments/starter_benchmark_campaign.yaml
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run-benchmark-campaign --config configs/experiments/moderate_benchmark_campaign.yaml
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run-benchmark-campaign --config configs/experiments/backend_benchmark_campaign.yaml
```
