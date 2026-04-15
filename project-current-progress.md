# Current Project Progress

## Handoff summary

The repository is currently at a stable intermediate stage.

- The core modeling foundation is implemented.
- The first classical vertical slice works end to end for MaxCut.
- The first quantum vertical slice also works end to end for MaxCut via exact-statevector QAOA.
- A config-driven Milestone 7 workflow now compares QAOA initialization strategies on that same MaxCut path.
- Later milestones such as MVC, VQE, shot-based/noisy backends, OpenJij, and landscape analysis are still deferred or scaffolded.

The current baseline that should be preserved is:

- `MaxCut -> QUBO -> Ising -> brute force -> saved outputs`
- `MaxCut -> QUBO -> Ising -> QAOA (statevector) -> saved outputs`
- `MaxCut -> QAOA initialization comparison (interpolation / warm_start / random) -> saved summary, traces, and plots`

Do not break those two validated paths in future passes.

## Milestone coverage

### Fully covered

- `Milestone 0: Repository foundation`
  - installable `src/` package
  - `pyproject.toml`
  - `tests/`
  - `configs/`
  - CLI entrypoint
- `Milestone 1: Core data structures`
  - `QUBOModel`
  - `IsingModel`
  - `DecodedSolution`
  - `SolverResult`
  - `SolverTraceEntry`
- `Milestone 2: QUBO to Ising conversion`
  - converter implementation
  - validation tests
- `Milestone 3: MaxCut problem module`
  - graph generation
  - QUBO encoding
  - decoding
  - objective evaluation
  - plot support
- `Milestone 4: Classical truth baseline`
  - brute-force exact solver
- `Milestone 6: QAOA exact-statevector implementation`
  - QAOA circuit builder
  - exact expectation evaluation
  - optimizer integration
  - initialization support
  - trace logging
  - runnable MaxCut example
- `Milestone 7: QAOA initialization strategies`
  - `random`, `interpolation`, and `warm_start` are all runnable
  - warm-start now accepts lower-depth optimized parameters end to end
  - config-driven comparison workflow exists:
    - `python -m qubo_vqa.cli compare-initializations --config ...`
  - comparison outputs include grouped summary metrics, per-run traces, and trace plots

### Partially covered

- `Milestone 5: Experiment runner and logging`
  - config-driven runner exists
  - run folders are timestamped and consistent
  - outputs include:
    - `config.json`
    - `result.json`
    - `metrics.json`
    - `run_metadata.json`
    - `trace.json`
    - `artifacts/qubo_model.json`
    - `artifacts/ising_model.json` for quantum runs
    - plots
  - not yet covered:
    - CSV histories
    - multi-run sweep structure
    - richer benchmark aggregation
- `Milestone 8: Plotting and benchmark metrics`
  - basic energy-trace and partition plots exist
  - initialization comparison outputs now include grouped summaries and per-run trace plots
  - publication-style benchmark plots and summary tables do not yet exist

### Scaffolded only

- `Milestone 9: Minimum Vertex Cover`
- `Milestone 10: VQE exact-statevector`
- `Milestone 11: Shot-based and noisy evaluation`
- `Milestone 12: Landscape analysis`
- `Milestone 13+:` later benchmark and interpretation milestones

## What works end to end right now

### Classical validated path

- problem: MaxCut
- encoding: QUBO
- solver: brute force
- output: decoded solution, metrics, run metadata, trace, QUBO artifact, plots

### Quantum validated path

- problem: MaxCut
- encoding: QUBO -> Ising
- solver: exact-statevector QAOA
- optimizer: SciPy through configurable optimizer settings
- output: decoded solution, metrics, run metadata, trace, QUBO artifact, Ising artifact, plots

### Initialization comparison validated path

- problem: MaxCut
- solver family: exact-statevector QAOA
- compared strategies: `interpolation`, `warm_start`, `random`
- output: `summary.json`, per-run `traces/*.json`, per-run energy-trace plots, QUBO artifact
- behavior validated in the current pass:
  - warm-start at higher depth consumes previous optimized parameters
  - all strategy/depth groups in the starter 4-cycle comparison recovered objective value `4.0`

## Current limitations

- Only `MaxCut` is actually implemented as a working problem.
- `MinimumVertexCoverInstance` and `TravelingSalesmanInstance` are scaffolds only.
- `VQESolver` is still a scaffold.
- QAOA currently supports only exact-statevector execution.
- The initialization comparison workflow is currently limited to the MaxCut statevector path.
- Some deeper QAOA comparison runs can hit the optimizer iteration cap before reporting `optimization_success=true`, even when the best decoded bitstring is already optimal.
- Shot-based and noisy execution are not implemented yet.
- Experiment configs are plain YAML; Hydra is not in use yet.
- Logging is good for single runs, but sweep/benchmark management is still minimal.
- Tests are meaningful for the current scope, but they do not yet cover reproducibility tolerances, MVC, VQE, or noisy backends.

## Important assumptions and design decisions

- `project-milestones.md` is the implementation-order source of truth.
- `project-explanation.md` is used for architecture and design interpretation.
- QUBO remains the canonical internal representation.
- The first quantum path uses a custom transparent QAOA implementation instead of a higher-level black-box wrapper.
- QAOA parameter order is:
  - `[gamma_0..gamma_{p-1}, beta_0..beta_{p-1}]`
- Warm-start interpolation is allowed from any strictly smaller QAOA depth, not only depth `p-1`.
- `qiskit` and `qiskit-aer` remain optional extras in `pyproject.toml`.
- `requirements.txt` currently installs the full local development environment with quantum support:
  - `-e .[dev,quantum]`
- TSP is intentionally deferred until MVC and the solver/experiment core are more mature.

## Exact validated commands

These commands were revalidated using the repository virtual environment and should be preserved for handoff:

### Install / sync environment

```powershell
& ".\.venv\Scripts\python.exe" -m pip install -e .[dev,quantum]
```

### Run tests

```powershell
& ".\.venv\Scripts\python.exe" -m pytest
```

Outcome at last validation:

- `8 passed`

### Run the classical MaxCut example

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/classical_maxcut.yaml
```

Outcome at last validation:

- command succeeded
- wrote a timestamped folder under `data/results/`

### Run the QAOA MaxCut example

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/qaoa_maxcut_statevector.yaml
```

Outcome at last validation:

- command succeeded
- wrote a timestamped folder under `data/results/`
- recovered the optimal cut value `4.0` on the 4-cycle example

### Run the QAOA initialization comparison example

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli compare-initializations --config configs/experiments/qaoa_initialization_comparison.yaml
```

Outcome at last validation:

- command succeeded
- wrote a timestamped folder under `data/results/`
- saved `summary.json`, `traces/`, and per-run energy-trace plots
- all starter comparison groups reached objective value `4.0` on the 4-cycle example
- the current summary showed strongest depth-2 expectation from `warm_start`:
  - `warm_start rep=2`: about `-3.9948`
  - `interpolation rep=2`: about `-3.4031`
  - `random rep=2` mean: about `-3.1162`

### Run lint/integrity check

```powershell
& ".\.venv\Scripts\python.exe" -m ruff check src tests
```

Outcome at last validation:

- passed after cleanup during the handoff audit

## What a new agent should preserve

- Keep the current package layout and modular boundaries.
- Keep `run_experiment_from_config()` as the main run entry point unless there is a strong reason to change it.
- Keep the current CLI command path working:
  - `python -m qubo_vqa.cli run --config ...`
- Keep the initialization comparison command working:
  - `python -m qubo_vqa.cli compare-initializations --config ...`
- Keep the current output-folder structure compatible with existing examples.
- Keep the current classical and QAOA MaxCut examples working while extending later milestones.
- Keep warm-start behavior tied to previously optimized lower-depth parameters unless there is a strong reason to change it.

## What remains next

The exact next milestone is:

- `Milestone 8: Plotting and benchmark metrics`

The most natural next implementation pass is:

1. strengthen `Milestone 8` by turning the initialization comparison outputs into clearer benchmark tables/plots,
2. then implement `Milestone 9` Minimum Vertex Cover on the same pipeline,
3. then move to `Milestone 10` VQE,
4. only after that expand into shot-based/noisy and landscape milestones.
