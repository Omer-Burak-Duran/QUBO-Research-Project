# QUBO-Research-Project

Research-oriented Python codebase for:

- transparent QUBO modeling of benchmark combinatorial problems,
- classical and quantum solver comparisons on shared encodings,
- reproducible experiment execution and artifact saving,
- optimization-landscape analysis for QAOA and VQE.

## Current foundation

This repository currently implements the first clean vertical slice:

- canonical `QUBOModel`, `IsingModel`, and standardized result containers,
- QUBO-to-Ising conversion utilities,
- a complete `MaxCut` benchmark encoder and decoder,
- an exact brute-force classical baseline,
- a config-driven experiment runner with saved JSON artifacts and plots,
- an exact-statevector QAOA path for small MaxCut instances,
- a config-driven QAOA initialization comparison workflow,
- standard QAOA comparison tables and benchmark-style plots for the current MaxCut path,
- starter scaffolding for later VQE, MVC, TSP, and landscape work.

## Installation

```bash
pip install -e .[dev,quantum]
```

If you only need the classical baseline path, `pip install -e .[dev]` is enough.

## Run the first example

```bash
python -m qubo_vqa.cli run --config configs/experiments/classical_maxcut.yaml
```

## Run the QAOA example

```bash
python -m qubo_vqa.cli run --config configs/experiments/qaoa_maxcut_statevector.yaml
```

## Compare QAOA initialization strategies

```bash
python -m qubo_vqa.cli compare-initializations --config configs/experiments/qaoa_initialization_comparison.yaml
```

This comparison command benchmarks `interpolation`, `warm_start`, and `random`
initialization on the current MaxCut statevector path and saves grouped metrics,
CSV tables, per-run traces, and benchmark-style plots under `data/results/`.

## Run the tests

```bash
pytest
```

The validated repository commands in this project have been run through the virtual environment interpreter:

```powershell
& ".\.venv\Scripts\python.exe" -m pytest
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/classical_maxcut.yaml
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/qaoa_maxcut_statevector.yaml
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli compare-initializations --config configs/experiments/qaoa_initialization_comparison.yaml
```
