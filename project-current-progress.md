# Current Project Progress

## Handoff summary

The repository is currently at a stable intermediate stage with both classical and first-generation quantum paths working on the shared MaxCut encoding.

- The core modeling foundation is implemented.
- The classical vertical slices work end to end for both MaxCut and Minimum Vertex Cover.
- The first quantum MaxCut path works end to end through exact-statevector QAOA.
- The constrained MVC quantum path is now also preserved for exact-statevector QAOA.
- Exact-statevector VQE now works end to end on both MaxCut and a tiny MVC path.
- The QAOA initialization-comparison workflow remains working and still produces CSV summaries plus benchmark plots.
- Shot-based backend support is now implemented for the current small QAOA and VQE paths.
- Aer-backed noisy backend support is now implemented for the current small MaxCut QAOA and VQE paths.
- A config-driven backend comparison workflow now measures exact-vs-shot-based-vs-noisy behavior directly on the preserved MaxCut QAOA path.
- A first preserved Milestone 12 landscape-analysis workflow now exists for a small MaxCut QAOA/VQE study.
- An OpenJij classical baseline now works end to end on the preserved small MaxCut and MVC paths.
- A config-driven solver comparison workflow now benchmarks brute force, OpenJij, QAOA, and VQE on the shared MaxCut starter instance.
- Config-driven benchmark campaigns now cover preserved starter, broader moderate, and backend-focused benchmark slices for MaxCut and MVC with grouped aggregate tables plus interpretation notes.
- All 15 planned milestones are now covered at repository level; broader research-scale datasets and TSP completion remain future extensions rather than uncovered milestone work.

The current baseline that should be preserved is:

- `MaxCut -> QUBO -> brute force -> saved outputs`
- `Minimum Vertex Cover -> QUBO -> brute force -> saved outputs`
- `MaxCut -> QUBO -> Ising -> QAOA (statevector) -> saved outputs`
- `MaxCut -> QUBO -> Ising -> QAOA (shot_based) -> saved outputs`
- `MaxCut -> QUBO -> Ising -> QAOA (noisy) -> saved outputs`
- `Minimum Vertex Cover -> QUBO -> Ising -> QAOA (statevector) -> saved outputs`
- `MaxCut -> QUBO -> Ising -> VQE (statevector) -> saved outputs`
- `MaxCut -> QUBO -> Ising -> VQE (noisy) -> saved outputs`
- `Minimum Vertex Cover -> QUBO -> Ising -> VQE (statevector) -> saved outputs`
- `MaxCut -> backend comparison (statevector / shot_based / noisy) -> saved summary, tables, traces, and plots`
- `MaxCut -> QAOA initialization comparison (interpolation / warm_start / random) -> saved summary, traces, tables, and plots`
- `MaxCut -> landscape analysis (QAOA p=1 heatmap / QAOA multi-start / QAOA+VQE gradient statistics) -> saved summary, tables, traces, and plots`
- `MaxCut -> OpenJij -> saved outputs`
- `Minimum Vertex Cover -> OpenJij -> saved outputs`
- `MaxCut -> solver comparison (brute_force / openjij / qaoa / vqe) -> saved summary, tables, traces, and plots`
- `Benchmark campaigns -> starter + moderate + backend-focused MaxCut/MVC benchmark slices -> saved summary, grouped tables, notes, plots, and nested run artifacts`

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
  - original milestone done criterion is satisfied:
    - a MaxCut brute-force experiment can be launched from config and produces a clean result folder
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
- `Milestone 11: Shot-based and noisy evaluation`
  - backend abstraction now supports:
    - `statevector`
    - `shot_based`
    - `noisy`
  - backend metadata now records:
    - mode
    - shots
    - backend seed
    - noise model name
  - the same QAOA and VQE solver code now runs through exact, shot-based, and noisy backend configurations
  - validated configs now exist for:
    - shot-based QAOA MaxCut
    - shot-based VQE MaxCut
    - noisy QAOA MaxCut
    - noisy VQE MaxCut
  - a config-driven backend comparison workflow now saves grouped summary metrics, CSV tables, per-run traces, and backend-comparison plots
- `Milestone 12: Landscape analysis`
  - `analysis/landscape.py` now implements a real QAOA `p=1` parameter-grid evaluator plus landscape summarization utilities
  - `analysis/barren_plateau.py` now implements finite-difference gradient sampling and summary statistics
  - a config-driven landscape workflow now exists:
    - `python -m qubo_vqa.cli analyze-landscape --config ...`
  - the preserved starter workflow currently saves:
    - `summary.json`
    - `tables/qaoa_p1_landscape.csv`
    - `tables/qaoa_multistart_runs.csv`
    - `tables/qaoa_gradient_statistics.csv`
    - `tables/vqe_gradient_statistics.csv`
    - per-run QAOA multi-start traces
    - QAOA landscape heatmaps
    - QAOA multi-start convergence plot
    - QAOA and VQE gradient-norm plots
  - validated starter behavior in the current pass:
    - the exact-reference 4-cycle MaxCut optimum remained `4.0`
    - the QAOA `p=1` grid recovered a best expectation energy of about `-3.0`
    - the multi-start QAOA runs all preserved best decoded objective value `4.0`
    - both QAOA and VQE gradient-statistics summaries were emitted successfully
- `Milestone 13: OpenJij and additional classical sampling baselines`
  - `OpenJijSolver` now supports the preserved classical solver surface through the normal `run` command path
  - the solver currently supports:
    - `sa`
    - `sqa`
  - validated starter configs now exist for:
    - MaxCut
    - Minimum Vertex Cover
  - a config-driven solver comparison workflow now exists:
    - `python -m qubo_vqa.cli compare-solvers --config ...`
  - comparison outputs include:
    - `summary.json`
    - `tables/run_metrics.csv`
    - `tables/aggregate_metrics.csv`
    - per-run solver traces
    - solver-comparison plots
  - validated Milestone 13 done criterion in the current pass:
    - for the starter MaxCut family, brute force, OpenJij, QAOA, and VQE all produced comparable result records and comparison tables
    - the shared comparison summary recorded objective value `4.0` for all four solver families on the preserved 4-cycle instance

- `Milestone 14: Full benchmark campaign`
  - `experiments/sweeps.py` now provides a config-driven benchmark campaign workflow
  - campaigns now support both:
    - explicit problem/solver cases
    - sweep-expanded problem/solver definitions with product or zip expansion
  - campaigns reuse the preserved problem/solver builders and standard per-run artifact writer
  - outputs now include:
    - nested per-run result folders under `runs/`
    - `tables/run_metrics.csv`
    - `tables/case_aggregates.csv`
    - `tables/solver_family_aggregates.csv`
    - `tables/problem_references.csv`
    - `tables/problem_family_aggregates.csv`
    - `tables/problem_size_aggregates.csv`
    - `tables/backend_aggregates.csv`
    - `tables/qaoa_depth_aggregates.csv`
    - `tables/vqe_depth_aggregates.csv`
    - benchmark aggregate plots
    - `notes.md`
  - validated campaign configs now exist:
    - `configs/experiments/starter_benchmark_campaign.yaml`
    - `configs/experiments/moderate_benchmark_campaign.yaml`
    - `configs/experiments/backend_benchmark_campaign.yaml`
  - validated repository-level behavior in the current pass:
    - the starter campaign executed `2` preserved problem cases across `6` solver cases for `12` total runs
    - the moderate campaign executed `6` problem cases across `8` solver cases for `48` total runs
    - the backend-focused campaign executed `2` problem cases across `8` solver cases for `16` total runs
    - all validated campaign commands emitted grouped tables, notes, plots, and nested run artifacts successfully
- `Milestone 15: Final interpretation layer`
  - the benchmark campaign now emits a repository-level interpretation layer through:
    - `summary.json`
    - `notes.md`
  - the current interpretation summarizes:
    - encoding stability
    - best solver per problem
    - QAOA vs VQE comparisons
    - structured vs hardware-efficient VQE comparisons
    - QAOA initialization comparisons
    - grouped scaling slices by problem size
    - backend-effect summaries
    - status-vs-solution-quality gaps
    - bottleneck cases
    - optional linked landscape-summary context
  - validated interpretation signal in the current pass:
    - the moderate and backend-focused campaigns both emitted the richer grouped aggregate sections in `summary.json`
    - the interpretation notes now expose real status-quality gaps for cases where decoded solution quality and optimizer-reported success diverge
    - backend-focused summaries now compare statevector, shot-based, and noisy benchmark slices directly

### Milestone Status Check

- `Milestones 0` through `15` are now implemented and fully covered at repository level against the intended definitions in `project-milestones.md`.

### Scaffolded only

- TSP remains intentionally deferred as a future benchmark extension
- broader report-scale or publication-scale campaign datasets remain optional follow-on work

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

### QAOA shot-based validated path

- problem: MaxCut
- encoding: QUBO -> Ising
- solver: finite-shot QAOA with a reproducible sampled backend
- validated starter config:
  - `configs/experiments/qaoa_maxcut_shot_based.yaml`
- validated behavior in the current pass:
  - the starter 4-cycle example recovered the optimal cut value `4.0`
  - the validated shot-based config finished with `optimization_success=true`
  - the recorded best expectation energy was about `-3.0127` at `4096` shots with backend seed `7`
- output: decoded solution, metrics, run metadata, trace, QUBO artifact, Ising artifact, plots

### QAOA noisy validated path

- problem: MaxCut
- encoding: QUBO -> Ising
- solver: noisy Aer-backed finite-shot QAOA
- validated starter config:
  - `configs/experiments/qaoa_maxcut_noisy.yaml`
- validated behavior in the current pass:
  - the starter 4-cycle example recovered the optimal cut value `4.0`
  - the validated noisy config finished with `optimization_success=true`
  - the recorded best expectation energy was about `-2.8701` at `4096` shots with noise model `depolarizing_readout`
- output: decoded solution, metrics, run metadata, trace, QUBO artifact, Ising artifact, plots

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

### VQE shot-based runnable path

- problem: MaxCut
- encoding: QUBO -> Ising
- solver: finite-shot VQE with a reproducible sampled backend
- validated starter config:
  - `configs/experiments/vqe_maxcut_shot_based.yaml`
- validated behavior in the current pass:
  - the starter config command succeeded and wrote the standard quantum artifact set
  - the validated shot-based config finished with `optimization_success=true`
  - with the current starter seed/config, the best decoded cut value was `2.0` rather than the exact optimum `4.0`
- output: decoded solution, metrics, run metadata, trace, QUBO artifact, Ising artifact, plots
- interpretation for handoff:
  - treat this as a runnable Milestone 11 starter path, not yet as a strong preserved benchmark baseline

### VQE noisy validated path

- problem: MaxCut
- encoding: QUBO -> Ising
- solver: noisy Aer-backed finite-shot VQE
- validated starter config:
  - `configs/experiments/vqe_maxcut_noisy.yaml`
- validated behavior in the current pass:
  - the starter 4-cycle example recovered the optimal cut value `4.0`
  - the validated noisy config finished with `optimization_success=true`
  - the recorded best expectation energy was about `-2.8398` at `4096` shots with noise model `depolarizing_readout`
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

### Backend comparison validated path

- problem: MaxCut
- solver family: QAOA
- compared backends:
  - `statevector`
  - `shot_based`
  - `noisy`
- validated starter config:
  - `configs/experiments/qaoa_backend_comparison.yaml`
- output:
  - `summary.json`
  - `tables/run_metrics.csv`
  - `tables/aggregate_metrics.csv`
  - per-run `traces/*.json`
  - per-run energy-trace plots
  - aggregate backend-comparison plots
- behavior validated in the current pass:
  - all three backend modes recovered objective value `4.0` on the starter 4-cycle example
  - the comparison directly showed expectation-energy degradation:
    - `statevector`: about `-3.0000`
    - `shot_based`: about `-2.9961`
    - `noisy`: about `-2.8594`
  - the noisy backend incurred a runtime cost relative to the current shot-based starter path

### Landscape analysis validated path

- problem: MaxCut
- encoding: QUBO -> Ising
- workflow surface:
  - QAOA `p=1` landscape scan
  - QAOA multi-start convergence study
  - QAOA finite-difference gradient statistics
  - VQE finite-difference gradient statistics
- validated starter config:
  - `configs/experiments/qaoa_landscape_analysis.yaml`
- output:
  - `summary.json`
  - `tables/qaoa_p1_landscape.csv`
  - `tables/qaoa_multistart_runs.csv`
  - `tables/qaoa_gradient_statistics.csv`
  - `tables/vqe_gradient_statistics.csv`
  - per-run `traces/qaoa-multistart-*.json`
  - `plots/qaoa_p1_landscape_energy.png`
  - `plots/qaoa_p1_landscape_objective.png`
  - `plots/qaoa_multistart_convergence.png`
  - `plots/qaoa_gradient_norms.png`
  - `plots/vqe_gradient_norms.png`
- behavior validated in the current pass:
  - the exact-reference 4-cycle MaxCut optimum remained `4.0`
  - the QAOA `p=1` scan covered `441` parameter points
  - the best sampled landscape point reached expectation energy about `-3.0`
  - the best sampled landscape point had:
    - `gamma`: about `0.7854`
    - `beta`: about `1.1781`
  - the multi-start QAOA summary preserved best decoded objective value `4.0`
  - the current summary reported:
    - mean QAOA gradient norm: about `2.1205`
    - mean VQE gradient norm: about `0.5977`

### OpenJij MaxCut validated path

- problem: MaxCut
- encoding: QUBO
- solver: OpenJij simulated annealing
- validated starter config:
  - `configs/experiments/openjij_maxcut.yaml`
- output: decoded solution, metrics, run metadata, trace, QUBO artifact, plots
- behavior validated in the current pass:
  - the starter 4-cycle example recovered the optimal cut value `4.0`
  - the recorded best QUBO energy was `-4.0`
  - the validated starter config emitted `64` sampled reads with sampler `sa`

### OpenJij Minimum Vertex Cover validated path

- problem: Minimum Vertex Cover
- encoding: QUBO with uncovered-edge penalties
- solver: OpenJij simulated annealing
- validated starter config:
  - `configs/experiments/openjij_min_vertex_cover.yaml`
- output: decoded solution, metrics, run metadata, trace, QUBO artifact, plots
- behavior validated in the current pass:
  - the starter 4-cycle example recovered a feasible cover of size `2`
  - the recorded best QUBO energy was `2.0`
  - the validated starter config emitted `64` sampled reads with sampler `sa`

### Cross-solver comparison validated path

- problem: MaxCut
- compared solver families:
  - `brute_force`
  - `openjij`
  - `qaoa`
  - `vqe`
- validated starter config:
  - `configs/experiments/maxcut_solver_comparison.yaml`
- output:
  - `summary.json`
  - `tables/run_metrics.csv`
  - `tables/aggregate_metrics.csv`
  - per-run `traces/*.json`
  - per-run energy-trace plots
  - aggregate solver-comparison plots
- behavior validated in the current pass:
  - all four solver families recovered objective value `4.0` on the starter 4-cycle example
  - the comparison summary recorded success rate `1.0` for all four validated solver cases
  - the current summary showed the following mean runtimes:
    - `brute_force`: about `0.0005 s`
    - `openjij`: about `0.1394 s`
    - `qaoa`: about `0.3711 s`
    - `vqe`: about `0.0358 s`

### Benchmark campaign validated path

- workflow surface:
  - `python -m qubo_vqa.cli run-benchmark-campaign --config ...`
- validated campaign configs:
  - `configs/experiments/starter_benchmark_campaign.yaml`
  - `configs/experiments/moderate_benchmark_campaign.yaml`
  - `configs/experiments/backend_benchmark_campaign.yaml`
- output:
  - `summary.json`
  - `notes.md`
  - `tables/run_metrics.csv`
  - `tables/case_aggregates.csv`
  - `tables/solver_family_aggregates.csv`
  - `tables/problem_references.csv`
  - `tables/problem_family_aggregates.csv`
  - `tables/problem_size_aggregates.csv`
  - `tables/backend_aggregates.csv`
  - `tables/qaoa_depth_aggregates.csv`
  - `tables/vqe_depth_aggregates.csv`
  - `plots/optimality_ratio_by_case.png`
  - `plots/runtime_by_case.png`
  - `plots/optimality_ratio_by_solver_family.png`
  - `plots/optimality_ratio_by_problem_family.png`
  - `plots/optimality_ratio_by_backend.png`
  - nested per-run artifacts under `runs/`
- behavior validated in the current pass:
  - the starter campaign executed `12` total runs across `2` problem cases and `6` solver cases
  - the moderate campaign executed `48` total runs across `6` problem cases and `8` solver cases
  - the backend-focused campaign executed `16` total runs across `2` problem cases and `8` solver cases
  - the moderate campaign emitted grouped slices over:
    - problem family
    - problem size
    - backend mode
    - QAOA depth
    - VQE depth
  - the backend-focused campaign emitted direct statevector / shot-based / noisy summaries on shared MaxCut and MVC cases
  - the generated interpretation notes now expose status-quality gaps rather than collapsing them into one success signal

## Current limitations

- `MaxCut` and `MinimumVertexCoverInstance` are currently implemented as working problems.
- QAOA and VQE currently support:
  - exact-statevector execution
  - noiseless finite-shot sampling
  - Aer-backed noisy finite-shot sampling
- The current `shot_based` backend samples from the exact computational-basis distribution with a seeded multinomial draw.
- The current noisy backend uses a small named noise-model registry rather than a fully general noise-model configuration layer.
- The initialization comparison workflow is currently limited to the MaxCut QAOA statevector path.
- The backend comparison workflow is currently validated on the MaxCut QAOA path.
- Milestone 8 plots currently summarize one benchmark instance/config at a time rather than a broader multi-instance campaign.
- The preserved Milestone 12 workflow is currently validated on a small MaxCut cycle instance with `qaoa.reps = 1`.
- The current landscape workflow supports the shared backend abstraction, but the preserved starter config is statevector-only.
- QAOA `p=2` slices and broader multi-instance landscape campaigns are still deferred beyond the first preserved landscape path.
- The preserved OpenJij benchmark path is currently validated with the `sa` sampler on small starter instances; `sqa` support exists but is not yet a preserved benchmark reference.
- The cross-solver comparison workflow is currently validated on the MaxCut starter family only.
- Some deeper QAOA comparison runs can hit the optimizer iteration cap before reporting `optimization_success=true`, even when the best decoded bitstring is already optimal.
- The current preserved finite-shot benchmark path is QAOA on MaxCut; shot-based VQE is runnable but still needs tuning before it should be treated as equally strong.
- In the benchmark campaigns, optimizer-reported success can still diverge from decoded solution quality, especially for some VQE and deeper QAOA cases.
- Benchmark campaigns are now repository-complete, but still intentionally moderate in size; they are not meant to be final publication-scale sweeps checked into the repository.
- Experiment configs are plain YAML; Hydra is not in use yet.
- Logging is good for single runs, but sweep/benchmark management is still minimal.
- Tests are meaningful for the current scope and now include shot-based, noisy, first-pass landscape-analysis, OpenJij, solver-comparison, benchmark-campaign, and campaign-summary coverage.

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
- Supported quantum backend modes are currently:
  - `statevector`
  - `shot_based`
  - `noisy`
- `shot_based` currently means seeded multinomial sampling from the exact noiseless basis distribution.
- `noisy` currently means Aer-backed finite-shot simulation with a named noise model.
- OpenJij is now the preserved classical sampling baseline for the current milestone-13 paths.
- The benchmark campaign normalizes semantic objective quality with an `optimality_ratio` metric:
  - maximization problems use `objective / optimum`
  - minimization problems use `optimum / objective`
- Solver completion and solution quality are now tracked separately in benchmark campaigns:
  - `solver_success` reflects optimizer/sampler completion status
  - `solution_quality_success` reflects whether the decoded solution reached the exact-reference optimum when available
- `qiskit` and `qiskit-aer` remain optional extras in `pyproject.toml`.
- `openjij` remains an optional extra under the classical dependency group in `pyproject.toml`.
- `requirements.txt` currently installs the full local development environment with quantum support:
  - `-e .[dev,classical,quantum]`
- TSP is intentionally deferred until the solver/experiment core is more mature.

## Exact validated commands

These commands were revalidated using the repository virtual environment and should be preserved for handoff:

### Install / sync environment

```powershell
& ".\.venv\Scripts\python.exe" -m pip install -e .[dev,classical,quantum]
```

### Run tests

```powershell
& ".\.venv\Scripts\python.exe" -m pytest
```

Outcome at last validation:

- `44 passed`

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

### Run the shot-based QAOA MaxCut example

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/qaoa_maxcut_shot_based.yaml
```

Outcome at last validation:

- command succeeded
- wrote a timestamped folder under `data/results/`
- recovered the optimal cut value `4.0` on the 4-cycle example
- finished with `optimization_success=true`
- recorded best expectation energy about `-3.0127` at `4096` shots with backend seed `7`

### Run the shot-based VQE MaxCut example

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/vqe_maxcut_shot_based.yaml
```

Outcome at last validation:

- command succeeded
- wrote a timestamped folder under `data/results/`
- finished with `optimization_success=true`
- recovered a feasible cut value `2.0` on the current starter seed/config
- this config is currently best treated as a runnable Milestone 11 starter, not yet as a preserved strong benchmark reference

### Run the noisy QAOA MaxCut example

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/qaoa_maxcut_noisy.yaml
```

Outcome at last validation:

- command succeeded
- wrote a timestamped folder under `data/results/`
- recovered the optimal cut value `4.0` on the 4-cycle example
- finished with `optimization_success=true`
- recorded best expectation energy about `-2.8701` at `4096` shots with noise model `depolarizing_readout`

### Run the noisy VQE MaxCut example

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/vqe_maxcut_noisy.yaml
```

Outcome at last validation:

- command succeeded
- wrote a timestamped folder under `data/results/`
- recovered the optimal cut value `4.0` on the 4-cycle example
- finished with `optimization_success=true`
- recorded best expectation energy about `-2.8398` at `4096` shots with noise model `depolarizing_readout`

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

### Run the backend comparison example

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli compare-backends --config configs/experiments/qaoa_backend_comparison.yaml
```

Outcome at last validation:

- command succeeded
- wrote a timestamped folder under `data/results/`
- saved `summary.json`, `tables/`, `traces/`, and both per-run plus aggregate backend plots
- all starter backend modes reached objective value `4.0` on the 4-cycle example
- the current summary showed backend sensitivity in expectation energy:
  - `statevector`: about `-3.0000`
  - `shot_based`: about `-2.9961`
  - `noisy`: about `-2.8594`

### Run the OpenJij MaxCut example

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/openjij_maxcut.yaml
```

Outcome at last validation:

- command succeeded
- wrote a timestamped folder under `data/results/`
- recovered the optimal cut value `4.0` on the 4-cycle example
- recorded best QUBO energy `-4.0`
- emitted `64` sampled reads with sampler `sa`

### Run the OpenJij Minimum Vertex Cover example

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/openjij_min_vertex_cover.yaml
```

Outcome at last validation:

- command succeeded
- wrote a timestamped folder under `data/results/`
- recovered a feasible cycle-graph cover of size `2`
- recorded best QUBO energy `2.0`
- emitted `64` sampled reads with sampler `sa`

### Run the landscape-analysis example

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli analyze-landscape --config configs/experiments/qaoa_landscape_analysis.yaml
```

Outcome at last validation:

- command succeeded
- wrote a timestamped folder under `data/results/`
- the exact-reference 4-cycle MaxCut optimum remained `4.0`
- the QAOA `p=1` scan covered `441` parameter points
- the best sampled landscape point reached expectation energy about `-3.0`
- the multi-start QAOA summary preserved best decoded objective value `4.0`
- both QAOA and VQE gradient-statistics tables and plots were emitted successfully

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

### Run the solver-comparison example

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli compare-solvers --config configs/experiments/maxcut_solver_comparison.yaml
```

Outcome at last validation:

- command succeeded
- wrote a timestamped folder under `data/results/`
- saved `summary.json`, `tables/`, `traces/`, and both per-run plus aggregate plots
- all four validated solver families recovered objective value `4.0` on the 4-cycle example:
  - `brute_force`
  - `openjij`
  - `qaoa`
  - `vqe`
- the comparison summary recorded success rate `1.0` for all four validated solver cases

### Run the benchmark-campaign example

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run-benchmark-campaign --config configs/experiments/starter_benchmark_campaign.yaml
```

Outcome at last validation:

- command succeeded
- wrote a timestamped folder under `data/results/`
- executed `12` benchmark runs across `2` preserved problem cases and `6` solver cases
- all starter runs recovered the optimal decoded objective value on the preserved cases
- emitted aggregate tables, interpretation notes, benchmark plots, and nested per-run result artifacts
- exposed the current VQE status limitation:
  - decoded objectives were optimal
  - `optimization_success` remained `false` on the starter VQE campaign cases

### Run the moderate benchmark-campaign example

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run-benchmark-campaign --config configs/experiments/moderate_benchmark_campaign.yaml
```

Outcome at last validation:

- command succeeded
- wrote a timestamped folder under `data/results/`
- executed `48` benchmark runs across `6` problem cases and `8` solver cases
- emitted grouped benchmark tables over problem family, problem size, backend mode, QAOA depth, and VQE depth
- produced interpretation notes exposing optimizer-status vs decoded-solution-quality gaps on the broader statevector benchmark slice

### Run the backend benchmark-campaign example

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run-benchmark-campaign --config configs/experiments/backend_benchmark_campaign.yaml
```

Outcome at last validation:

- command succeeded
- wrote a timestamped folder under `data/results/`
- executed `16` benchmark runs across `2` problem cases and `8` solver cases
- produced direct benchmark summaries for:
  - `statevector`
  - `shot_based`
  - `noisy`
- emitted backend aggregate tables and benchmark plots for the preserved small MaxCut and MVC backend slice

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
- Keep the current shot-based QAOA MaxCut example working:
  - `python -m qubo_vqa.cli run --config configs/experiments/qaoa_maxcut_shot_based.yaml`
- Keep the current noisy MaxCut examples working:
  - `python -m qubo_vqa.cli run --config configs/experiments/qaoa_maxcut_noisy.yaml`
  - `python -m qubo_vqa.cli run --config configs/experiments/vqe_maxcut_noisy.yaml`
- Keep the current shot-based backend toggle working through `solver.parameters.backend`.
- Keep the current backend comparison command working:
  - `python -m qubo_vqa.cli compare-backends --config configs/experiments/qaoa_backend_comparison.yaml`
- Keep the new landscape-analysis command working:
  - `python -m qubo_vqa.cli analyze-landscape --config configs/experiments/qaoa_landscape_analysis.yaml`
- Keep the OpenJij example commands working:
  - `python -m qubo_vqa.cli run --config configs/experiments/openjij_maxcut.yaml`
  - `python -m qubo_vqa.cli run --config configs/experiments/openjij_min_vertex_cover.yaml`
- Keep the solver-comparison command working:
  - `python -m qubo_vqa.cli compare-solvers --config configs/experiments/maxcut_solver_comparison.yaml`
- Keep the benchmark-campaign command working:
  - `python -m qubo_vqa.cli run-benchmark-campaign --config configs/experiments/starter_benchmark_campaign.yaml`
  - `python -m qubo_vqa.cli run-benchmark-campaign --config configs/experiments/moderate_benchmark_campaign.yaml`
  - `python -m qubo_vqa.cli run-benchmark-campaign --config configs/experiments/backend_benchmark_campaign.yaml`
- Keep the preserved MVC quantum example paths working:
  - `python -m qubo_vqa.cli run --config configs/experiments/qaoa_min_vertex_cover_statevector.yaml`
  - `python -m qubo_vqa.cli run --config configs/experiments/vqe_min_vertex_cover_statevector.yaml`
- Keep warm-start behavior tied to previously optimized lower-depth parameters unless there is a strong reason to change it.
- Keep VQE ansatz configuration nested under `solver.parameters.ansatz` unless there is a strong reason to change the config shape.

## What remains next

All planned milestones are now covered at repository level.

The most natural next implementation passes are optional extensions beyond the 15-milestone plan:

1. broaden benchmark campaigns toward larger publication-scale datasets and more graph families,
2. improve VQE optimizer-status handling so success metrics align more cleanly with decoded solution quality,
3. deepen automatic linkage between campaign summaries and landscape-analysis outputs,
4. add stronger sweep-management ergonomics if campaigns become much larger than the current repository-level validation set.

## Experiment and report stage

The repository has now also been taken through an experiment-and-report pass grounded in fresh local executions rather than assumed historical outputs.

### Artifacts created

- `how-to-run.md`
- `project-report.md`

### Validation and experiment session used for the report

The report-stage outputs were generated under:

- `data/results/session-20260415/`

Commands executed in this session:

- `& ".\.venv\Scripts\python.exe" -m pytest`
- `& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/classical_maxcut.yaml --output-dir data/results/session-20260415`
- `& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/classical_min_vertex_cover.yaml --output-dir data/results/session-20260415`
- `& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/qaoa_maxcut_statevector.yaml --output-dir data/results/session-20260415`
- `& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/vqe_maxcut_statevector.yaml --output-dir data/results/session-20260415`
- `& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/qaoa_min_vertex_cover_statevector.yaml --output-dir data/results/session-20260415`
- `& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run --config configs/experiments/vqe_min_vertex_cover_statevector.yaml --output-dir data/results/session-20260415`
- `& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli compare-solvers --config configs/experiments/maxcut_solver_comparison.yaml --output-dir data/results/session-20260415`
- `& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli compare-backends --config configs/experiments/qaoa_backend_comparison.yaml --output-dir data/results/session-20260415`
- `& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli compare-initializations --config configs/experiments/qaoa_initialization_comparison.yaml --output-dir data/results/session-20260415`
- `& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli analyze-landscape --config configs/experiments/qaoa_landscape_analysis.yaml --output-dir data/results/session-20260415`
- `& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run-benchmark-campaign --config configs/experiments/starter_benchmark_campaign.yaml --output-dir data/results/session-20260415`
- `& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run-benchmark-campaign --config configs/experiments/moderate_benchmark_campaign.yaml --output-dir data/results/session-20260415`
- `& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run-benchmark-campaign --config configs/experiments/backend_benchmark_campaign.yaml --output-dir data/results/session-20260415`

Observed outcomes in this pass:

- tests passed: `44 passed`
- all planned commands above completed successfully
- the report is based on fresh generated outputs, not checked-in result folders
- the strongest recurring interpretation caveat remains the optimizer-status vs decoded-solution-quality gap, especially in several VQE benchmark slices
- constrained Minimum Vertex Cover campaign rows should be read with feasibility and penalty fields, not only with `optimality_ratio`