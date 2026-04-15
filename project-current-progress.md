# Current Project Progress

## Handoff summary

The repository is currently at a stable intermediate stage with both classical and first-generation quantum paths working on the shared MaxCut encoding.

- The core modeling foundation is implemented.
- The classical vertical slices work end to end for both MaxCut and Minimum Vertex Cover.
- The first quantum MaxCut path works end to end through exact-statevector QAOA.
- The constrained MVC quantum path is now also preserved for exact-statevector QAOA.
- Exact-statevector VQE now works end to end on both MaxCut and a tiny MVC path.
- The QAOA initialization-comparison workflow remains working and still produces CSV summaries plus benchmark plots.
- Later milestones such as shot-based/noisy backends, OpenJij baselines, TSP completion, and landscape analysis are still deferred.

The current baseline that should be preserved is:

- `MaxCut -> QUBO -> brute force -> saved outputs`
- `Minimum Vertex Cover -> QUBO -> brute force -> saved outputs`
- `MaxCut -> QUBO -> Ising -> QAOA (statevector) -> saved outputs`
- `Minimum Vertex Cover -> QUBO -> Ising -> QAOA (statevector) -> saved outputs`
- `MaxCut -> QUBO -> Ising -> VQE (statevector) -> saved outputs`
- `Minimum Vertex Cover -> QUBO -> Ising -> VQE (statevector) -> saved outputs`
- `MaxCut -> QAOA initialization comparison (interpolation / warm_start / random) -> saved summary, traces, tables, and plots`

Do not break these validated paths in future passes.

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
  - warm-start accepts lower-depth optimized parameters end to end
  - config-driven comparison workflow exists:
    - `python -m qubo_vqa.cli compare-initializations --config ...`
  - comparison outputs include grouped summary metrics, per-run traces, and trace plots
- `Milestone 8: Plotting and benchmark metrics`
  - standard comparison plots exist for the current QAOA benchmark path:
    - approximation ratio vs depth
    - expectation energy vs depth
    - runtime vs depth
    - function evaluations vs depth
    - final parameter values by depth and strategy
  - exact-reference metrics are included:
    - brute-force optimum objective value
    - per-run approximation ratio
    - grouped success rates
  - CSV summary tables exist:
    - `tables/run_metrics.csv`
    - `tables/aggregate_metrics.csv`
- `Milestone 9: Minimum Vertex Cover`
  - QUBO encoding implemented with uncovered-edge penalties
  - decoder returns selected vertices, uncovered edges, cover size, and feasibility
  - brute-force validation added on tiny instances
  - config-driven classical MVC example runs through the current artifact pipeline
- `Milestone 10: VQE exact-statevector`
  - `VQESolver` is implemented on the same QUBO -> Ising boundary as QAOA
  - supported ansatz families:
    - `hardware_efficient`
    - `problem_aware`
  - validated VQE examples now exist for:
    - MaxCut
    - Minimum Vertex Cover
  - targeted VQE tests cover:
    - evaluation behavior
    - solver output shape
    - MVC feasibility on a preserved tiny instance
    - runner integration
  - side-by-side comparison path now exists through matched QAOA/VQE configs and shared result schema on tiny MaxCut and MVC examples
  - ansatz metadata, optimizer metadata, Ising artifact, and full evaluation trace are logged

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
    - CSV histories for single runs
    - multi-run sweep structure
    - richer benchmark aggregation outside the QAOA initialization workflow

### Scaffolded only

- `Milestone 11: Shot-based and noisy evaluation`
- `Milestone 12: Landscape analysis`
- `Milestone 13+:` later benchmark and interpretation milestones

## What works end to end right now

### Classical validated path

- problem: MaxCut
- encoding: QUBO
- solver: brute force
- output: decoded solution, metrics, run metadata, trace, QUBO artifact, plots

### Minimum Vertex Cover validated path

- problem: Minimum Vertex Cover
- encoding: QUBO with uncovered-edge penalties
- solver: brute force
- output: decoded solution, metrics, run metadata, trace, QUBO artifact, plots
- behavior validated in the current pass:
  - the starter 4-node path example recovered a feasible cover of size `2`
  - decoded penalty reporting matched uncovered-edge counts in tests

### QAOA validated path

- problem: MaxCut
- encoding: QUBO -> Ising
- solver: exact-statevector QAOA
- optimizer: SciPy through configurable optimizer settings
- output: decoded solution, metrics, run metadata, trace, QUBO artifact, Ising artifact, plots
- behavior validated in the current pass:
  - the starter 4-cycle example recovered the optimal cut value `4.0`

### QAOA MVC validated path

- problem: Minimum Vertex Cover
- encoding: QUBO -> Ising
- solver: exact-statevector QAOA
- validated starter config:
  - `configs/experiments/qaoa_min_vertex_cover_statevector.yaml`
- validated behavior in the current pass:
  - the starter 4-cycle example recovered a feasible cover of size `2`
  - the preserved QAOA config finished with `optimization_success=true`
- output: decoded solution, metrics, run metadata, trace, QUBO artifact, Ising artifact, plots

### VQE validated path

- problem: MaxCut
- encoding: QUBO -> Ising
- solver: exact-statevector VQE
- validated starter config:
  - `configs/experiments/vqe_maxcut_statevector.yaml`
- validated behavior in the current pass:
  - the starter 4-cycle example recovered the optimal cut value `4.0`
  - the validated problem-aware depth-1 config finished with `optimization_success=true`
  - the best expectation energy was about `-3.0`, consistent with the p=1-style symmetric optimum on this instance
- output: decoded solution, metrics, run metadata, trace, QUBO artifact, Ising artifact, plots

### VQE MVC validated path

- problem: Minimum Vertex Cover
- encoding: QUBO -> Ising
- solver: exact-statevector VQE
- validated starter config:
  - `configs/experiments/vqe_min_vertex_cover_statevector.yaml`
- validated behavior in the current pass:
  - the starter 4-cycle example recovered a feasible cover of size `2`
  - the validated hardware-efficient depth-1 config finished with `optimization_success=true`
  - the dominant basis probability exceeded `0.998` on the validated MVC example
- output: decoded solution, metrics, run metadata, trace, QUBO artifact, Ising artifact, plots

### Side-by-side variational comparison path

- shared tiny instances now exist for both:
  - MaxCut
  - Minimum Vertex Cover
- comparison surface:
  - same `python -m qubo_vqa.cli run --config ...` command path
  - same `SolverResult` schema
  - same `metrics.json` layout
  - same `trace.json` structure
- behavior validated in the current pass:
  - QAOA and VQE both recovered optimal MaxCut objective `4.0`
  - QAOA and VQE both recovered feasible MVC objective `2.0`

### Initialization comparison validated path

- problem: MaxCut
- solver family: exact-statevector QAOA
- compared strategies: `interpolation`, `warm_start`, `random`
- output:
  - `summary.json`
  - `tables/run_metrics.csv`
  - `tables/aggregate_metrics.csv`
  - per-run `traces/*.json`
  - per-run energy-trace plots
  - aggregate benchmark plots
  - QUBO artifact
- behavior validated in the current pass:
  - warm-start at higher depth consumes previous optimized parameters
  - all strategy/depth groups in the starter 4-cycle comparison recovered objective value `4.0`
  - exact optimum reference is recorded from brute force
  - depth-2 `warm_start` still gives the strongest expectation among starter runs

## Current limitations

- `MaxCut` and `MinimumVertexCoverInstance` are currently implemented as working problems.
- `TravelingSalesmanInstance` is still a scaffold.
- QAOA and VQE currently support only exact-statevector execution.
- The initialization comparison workflow is currently limited to the MaxCut QAOA statevector path.
- Milestone 8 plots currently summarize one benchmark instance/config at a time rather than a broader multi-instance campaign.
- Some deeper QAOA comparison runs can hit the optimizer iteration cap before reporting `optimization_success=true`, even when the best decoded bitstring is already optimal.
- Shot-based and noisy execution are not implemented yet.
- Experiment configs are plain YAML; Hydra is not in use yet.
- Logging is good for single runs, but sweep/benchmark management is still minimal.
- Tests are meaningful for the current scope, but they do not yet cover reproducibility tolerances, noisy backends, or landscape analysis.

## Important assumptions and design decisions

- `project-milestones.md` is the implementation-order source of truth.
- `project-explanation.md` is used for architecture and design interpretation, not as an exact file inventory.
- `project-current-progress.md` should be treated as the authoritative current-state handoff document.
- QUBO remains the canonical internal representation.
- The first quantum paths use custom transparent solver wrappers instead of higher-level black-box algorithm classes.
- QAOA parameter order is:
  - `[gamma_0..gamma_{p-1}, beta_0..beta_{p-1}]`
- Warm-start interpolation is allowed from any strictly smaller QAOA depth, not only depth `p-1`.
- The VQE `problem_aware` ansatz uses the Ising coupling structure plus per-qubit `RX` mixer angles.
- The VQE `hardware_efficient` ansatz uses `RY`/`RZ` layers with ring `CX` entanglement.
- `qiskit` and `qiskit-aer` remain optional extras in `pyproject.toml`.
- `requirements.txt` currently installs the full local development environment with quantum support:
  - `-e .[dev,quantum]`
- TSP is intentionally deferred until the solver/experiment core is more mature.

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

- `20 passed`

### Run the classical MaxCut example

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/classical_maxcut.yaml
```

Outcome at last validation:

- command succeeded
- wrote a timestamped folder under `data/results/`
- recovered the optimal cut value `4.0` on the 4-cycle example

### Run the QAOA MaxCut example

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/qaoa_maxcut_statevector.yaml
```

Outcome at last validation:

- command succeeded
- wrote a timestamped folder under `data/results/`
- recovered the optimal cut value `4.0` on the 4-cycle example

### Run the VQE MaxCut example

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/vqe_maxcut_statevector.yaml
```

Outcome at last validation:

- command succeeded
- wrote a timestamped folder under `data/results/`
- recovered the optimal cut value `4.0` on the 4-cycle example
- finished with `optimization_success=true` on the validated depth-1 problem-aware config

### Run the QAOA initialization comparison example

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli compare-initializations --config configs/experiments/qaoa_initialization_comparison.yaml
```

Outcome at last validation:

- command succeeded
- wrote a timestamped folder under `data/results/`
- saved `summary.json`, `tables/`, `traces/`, and both per-run plus aggregate plots
- all starter comparison groups reached objective value `4.0` on the 4-cycle example
- the current summary showed strongest depth-2 expectation from `warm_start`:
  - `warm_start rep=2`: about `-3.9948`
  - `interpolation rep=2`: about `-3.4031`
  - `random rep=2` mean: about `-3.1162`

### Run the classical Minimum Vertex Cover example

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/classical_min_vertex_cover.yaml
```

Outcome at last validation:

- command succeeded
- wrote a timestamped folder under `data/results/`
- recovered a feasible path-graph cover of size `2` with zero penalty

### Run the QAOA Minimum Vertex Cover example

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/qaoa_min_vertex_cover_statevector.yaml
```

Outcome at last validation:

- command succeeded
- wrote a timestamped folder under `data/results/`
- recovered a feasible cycle-graph cover of size `2`
- finished with `optimization_success=true`

### Run the VQE Minimum Vertex Cover example

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/vqe_min_vertex_cover_statevector.yaml
```

Outcome at last validation:

- command succeeded
- wrote a timestamped folder under `data/results/`
- recovered a feasible cycle-graph cover of size `2`
- finished with `optimization_success=true`
- concentrated more than `99.8%` probability on the optimal validated MVC bitstring

### Run lint/integrity check

```powershell
& ".\.venv\Scripts\python.exe" -m ruff check src tests
```

Outcome at last validation:

- passed

## What a new agent should preserve

- Keep the current package layout and modular boundaries.
- Keep `project-current-progress.md` aligned with the actual validated repository state.
- Keep `run_experiment_from_config()` as the main run entry point unless there is a strong reason to change it.
- Keep the current CLI command path working:
  - `python -m qubo_vqa.cli run --config ...`
- Keep the initialization comparison command working:
  - `python -m qubo_vqa.cli compare-initializations --config ...`
- Keep the current output-folder structure compatible with existing examples.
- Keep the current classical MVC example working:
  - `python -m qubo_vqa.cli run --config configs/experiments/classical_min_vertex_cover.yaml`
- Keep the current classical, QAOA, and VQE MaxCut examples working while extending later milestones.
- Keep the preserved MVC quantum example paths working:
  - `python -m qubo_vqa.cli run --config configs/experiments/qaoa_min_vertex_cover_statevector.yaml`
  - `python -m qubo_vqa.cli run --config configs/experiments/vqe_min_vertex_cover_statevector.yaml`
- Keep warm-start behavior tied to previously optimized lower-depth parameters unless there is a strong reason to change it.
- Keep VQE ansatz configuration nested under `solver.parameters.ansatz` unless there is a strong reason to change the config shape.

## What remains next

The exact next milestone is now:

- `Milestone 11: Shot-based and noisy quantum evaluation`

The most natural next implementation pass is:

1. extend the current backend abstraction beyond exact statevector into shot-based estimation,
2. reuse the existing QAOA and VQE solver interfaces for exact vs shot-based toggles,
3. add one preserved noiseless-vs-shot-based validation path before introducing Aer noise models,
4. only after that move into landscape-analysis milestones.
