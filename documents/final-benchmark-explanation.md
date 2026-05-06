# Final Benchmark Explanation

This document explains the final benchmark suite prepared for the final research report.
The suite is designed to generate all report-ready evidence from a single session under
`data/results/session-20260506/`.

The project scope for this run is:

- QUBO modeling for MaxCut and Minimum Vertex Cover;
- QUBO-to-Ising conversion for variational quantum algorithms;
- classical baselines with brute force and OpenJij;
- QAOA and VQE comparisons on shared encodings;
- backend behavior under exact statevector, finite-shot, and noisy simulation;
- initialization, depth, ansatz, and landscape analysis.

Traveling Salesman Problem experiments are intentionally out of scope. The codebase now exposes
only `MaxCutInstance` and `MinimumVertexCoverInstance` from the problem package.

## General Report Strategy

The final report should not treat one run as proving general quantum advantage. These benchmarks are
small, exact-reference, course-scale experiments. Their value is that they show a coherent pipeline:
problem encoding, QUBO inspection, Ising conversion, solver execution, artifact logging, and aggregate
analysis over controlled instances.

The most useful final-report structure is:

- use the main campaign for solver-family, problem-family, size, QAOA-depth, and VQE-ansatz tables;
- use the backend campaign for exact vs shot-based vs noisy behavior;
- use the QAOA initialization study for optimizer-start discussion;
- use the landscape study for visual and trainability discussion;
- use single per-run artifacts only as examples of the QUBO/Ising pipeline and decoded solutions.

## Preflight Validation

Command:

```powershell
& ".\.venv\Scripts\python.exe" -m pytest
```

Purpose:

The preflight confirms that the package imports, solver paths, config loaders, campaign aggregation,
and plotting/logging workflows are still internally consistent before spending time on the full run.

Current expected result:

```text
45 passed
```

Artifacts to keep:

- terminal output showing the passing test count;
- optionally a short note in the report methods section that tests passed before benchmark execution.

Remarks:

This is not experimental evidence by itself, but it is important reproducibility evidence. If tests fail,
do not run the final benchmark until the failure is understood.

## Main Statevector Campaign

Config:

```text
configs/experiments/final_report_benchmark_campaign.yaml
```

Command:

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run-benchmark-campaign --config configs/experiments/final_report_benchmark_campaign.yaml --output-dir data/results/session-20260506
```

Purpose:

This is the main final-report benchmark. It compares solver families on the same QUBO encodings while
keeping all quantum runs statevector-based. This isolates modeling, optimizer, depth, initialization,
and ansatz effects from backend sampling/noise effects.

Included problem cases:

- MaxCut cycle with 4 variables;
- MaxCut cycle with 6 variables;
- MaxCut Erdős-Rényi graph with 6 variables;
- weighted MaxCut Erdős-Rényi graph with 8 variables;
- Minimum Vertex Cover path with 4 variables;
- Minimum Vertex Cover cycle with 6 variables;
- Minimum Vertex Cover Erdős-Rényi graph with 6 variables;
- Minimum Vertex Cover Erdős-Rényi graph with 8 variables.

Included solver cases:

- brute force exact reference;
- OpenJij simulated annealing with repeated trials;
- QAOA with interpolation initialization at `p=1`;
- QAOA with interpolation initialization at `p=2`;
- QAOA with random initialization at `p=1`, repeated across seeds;
- QAOA with random initialization at `p=2`, repeated across seeds;
- VQE problem-aware ansatz at depth 1, repeated across seeds;
- VQE problem-aware ansatz at depth 2, repeated across seeds;
- VQE hardware-efficient ansatz at depth 1, repeated across seeds;
- VQE hardware-efficient ansatz at depth 2, repeated across seeds.

Validated scope:

- 8 problem cases;
- 10 solver cases;
- 152 total runs;
- exact references available for all selected cases.

Expected theoretical results and remarks:

- Brute force should always return the exact optimum and should be used as the reference, not as a scalable method.
- OpenJij should often find optimal or near-optimal solutions on these small cases, with some seed sensitivity on harder random graphs.
- QAOA at `p=2` should generally have a better or equal expectation-energy optimum than `p=1`, but decoded dominant-bitstring quality can still vary.
- Random QAOA starts should show optimizer sensitivity; interpolation is expected to be more stable but not always best.
- VQE depth 2 may improve expressivity but can also be harder for COBYLA because the parameter space is larger.
- Problem-aware VQE may benefit from Hamiltonian structure, while hardware-efficient VQE provides a less problem-specific ansatz comparison.
- The weighted 8-variable MaxCut case is expected to be harder and more informative than the unweighted cycles.
- For Minimum Vertex Cover, feasibility is essential. Campaign `optimality_ratio` is feasibility-adjusted, and raw objective-only quality is saved separately as `objective_optimality_ratio`.

Artifacts to save for the report:

- `summary.json` for exact problem references, aggregate summaries, and interpretation fields;
- `notes.md` for generated human-readable campaign notes;
- `tables/run_metrics.csv` for detailed per-run values;
- `tables/case_aggregates.csv` for case-by-solver comparisons;
- `tables/solver_family_aggregates.csv` for overall solver-family comparisons;
- `tables/problem_family_aggregates.csv` and `tables/problem_size_aggregates.csv` for scaling and problem-family discussion;
- `tables/qaoa_depth_aggregates.csv` for QAOA depth discussion;
- `tables/vqe_depth_aggregates.csv` for VQE ansatz/depth discussion;
- `plots/optimality_ratio_by_case.png`;
- `plots/runtime_by_case.png`;
- `plots/optimality_ratio_by_solver_family.png`;
- `plots/optimality_ratio_by_problem_family.png`;
- selected per-run `result.json`, `metrics.json`, `trace.json`, `artifacts/qubo_model.json`, and `artifacts/ising_model.json` as examples.

Best report uses:

- primary solver comparison table;
- MaxCut vs Minimum Vertex Cover discussion;
- feasibility-aware constrained optimization discussion;
- QAOA depth and initialization comparison;
- VQE ansatz and depth comparison;
- runtime and evaluation-count discussion.

## Backend Campaign

Config:

```text
configs/experiments/final_report_backend_campaign.yaml
```

Command:

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run-benchmark-campaign --config configs/experiments/final_report_backend_campaign.yaml --output-dir data/results/session-20260506
```

Purpose:

This campaign studies how backend execution mode changes the behavior of the same QAOA and VQE
solver paths. It is intentionally smaller than the main campaign because noisy Aer simulation is more
expensive and because backend effects are easiest to interpret on small instances.

Included problem cases:

- MaxCut cycle with 4 variables;
- MaxCut Erdős-Rényi graph with 6 variables;
- Minimum Vertex Cover cycle with 4 variables.

Included solver/backend cases:

- brute force reference;
- QAOA statevector;
- QAOA finite-shot sampling;
- QAOA noisy sampling with `depolarizing_readout`;
- VQE statevector;
- VQE finite-shot sampling;
- VQE noisy sampling with `depolarizing_readout`.

Validated scope:

- 3 problem cases;
- 7 solver cases;
- 39 total runs.

Expected theoretical results and remarks:

- Statevector mode should be the clean deterministic reference for the chosen variational parameters.
- Shot-based mode should introduce finite-sampling fluctuations in expectation estimates and dominant basis probabilities.
- Noisy mode should generally degrade expectation-energy estimates and increase runtime.
- Decoded objective values may remain optimal on very small instances even when expectation values degrade.
- The shot-based backend samples from exact noiseless probabilities, so it should be described as finite-shot statistical sampling, not as hardware noise.
- The noisy backend uses an Aer model and should be discussed as simulated device-like noise, not real hardware evidence.

Artifacts to save for the report:

- `tables/run_metrics.csv` for backend mode, shots, noise model, expectation energy, objective value, runtime, and feasibility;
- `tables/backend_aggregates.csv` for grouped backend comparisons;
- `summary.json` and `notes.md` for interpretation fields;
- `plots/optimality_ratio_by_backend.png`;
- selected per-run traces for statevector vs shot-based vs noisy examples;
- selected `result.json` files showing backend metadata, shot count, seed, and noise model.

Best report uses:

- backend comparison figure or table;
- expectation-energy degradation under noisy sampling;
- distinction between decoded objective quality and expectation quality;
- careful limitations statement about simulated noise and small problem size.

## QAOA Initialization Study

Config:

```text
configs/experiments/final_report_qaoa_initialization_comparison.yaml
```

Command:

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli compare-initializations --config configs/experiments/final_report_qaoa_initialization_comparison.yaml --output-dir data/results/session-20260506
```

Purpose:

This workflow isolates QAOA initialization effects on a 6-variable Erdős-Rényi MaxCut instance. It is
separate from the main campaign because warm-start initialization is sequential across depths and needs
a specialized workflow.

Included experiments:

- interpolation initialization at `p=1`, `p=2`, and `p=3`;
- warm-start initialization bootstrapped from interpolation and extended through `p=1`, `p=2`, and `p=3`;
- random initialization at `p=1`, `p=2`, and `p=3` with four random trials per depth.

Validated scope:

- 18 total QAOA runs.

Expected theoretical results and remarks:

- Increasing depth should improve the best achievable expectation energy in principle, but local optimizer behavior may prevent monotonic decoded quality.
- Warm-start should often provide more stable higher-depth starts because it reuses lower-depth optimized parameters.
- Random starts should expose optimizer sensitivity and local-minimum behavior.
- Optimizer success flags should be interpreted separately from decoded objective quality because COBYLA may hit iteration caps even when the decoded solution is good.

Artifacts to save for the report:

- `summary.json` for exact reference, run metrics, and aggregate metrics;
- `tables/run_metrics.csv` for individual initialization/depth/trial results;
- `tables/aggregate_metrics.csv` for mean approximation ratio, expectation energy, runtime, evaluations, and success rate by strategy/depth;
- `plots/approximation_ratio_vs_depth.png`;
- `plots/best_expectation_energy_vs_depth.png`;
- `plots/runtime_vs_depth.png`;
- `plots/evaluations_vs_depth.png`;
- QAOA parameter-value plots under `plots/`;
- per-run trace JSON files under `traces/`.

Best report uses:

- one plot comparing expectation energy by depth and strategy;
- one short table of aggregate metrics;
- discussion of why initialization matters even when small decoded objectives remain close to optimal.

## Landscape And Gradient Study

Config:

```text
configs/experiments/final_report_landscape_analysis.yaml
```

Command:

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli analyze-landscape --config configs/experiments/final_report_landscape_analysis.yaml --output-dir data/results/session-20260506
```

Purpose:

This workflow produces visual and numeric evidence about the optimization landscape. It focuses on the
same 6-variable Erdős-Rényi MaxCut case used by the initialization study, which makes the landscape and
initialization discussions consistent.

Included experiments:

- QAOA `p=1` grid scan over `gamma` and `beta`;
- QAOA multi-start optimization from six random starts;
- finite-difference QAOA gradient samples;
- finite-difference VQE gradient samples for a hardware-efficient depth-1 ansatz.

Validated scope:

- 961 QAOA landscape grid points;
- 6 QAOA multi-start runs;
- 12 QAOA gradient samples;
- 12 VQE gradient samples.

Expected theoretical results and remarks:

- The QAOA `p=1` landscape should show structured periodic behavior because the two-parameter circuit is low dimensional.
- Good grid regions should align with lower expectation energy, but dominant decoded objective can be piecewise constant across wide regions.
- Multi-start traces should show whether different initial points converge similarly or remain separated.
- Gradient statistics should be nonzero on these small instances; this is not expected to demonstrate a barren plateau, only a first-pass trainability comparison.
- VQE gradient norms may differ substantially from QAOA because the ansatz family and parameter count are different.

Artifacts to save for the report:

- `tables/qaoa_p1_landscape.csv` for grid-level expectation and decoded objective data;
- `tables/qaoa_multistart_runs.csv` for multi-start optimizer outcomes;
- `tables/qaoa_gradient_statistics.csv`;
- `tables/vqe_gradient_statistics.csv`;
- `summary.json` for best grid point, multi-start summary, and gradient summaries;
- `plots/qaoa_p1_landscape_energy.png`;
- `plots/qaoa_p1_landscape_objective.png`;
- `plots/qaoa_multistart_convergence.png`;
- `plots/qaoa_gradient_norms.png`;
- `plots/vqe_gradient_norms.png`;
- selected trace JSON files under `traces/`.

Best report uses:

- QAOA heatmap figure;
- multi-start convergence figure;
- gradient norm comparison table;
- discussion of trainability limitations at small scale.

## Cross-Campaign Values To Extract

For final writing, extract these values after all campaigns finish:

- test pass count and Python version;
- total number of runs in each campaign;
- problem labels, graph sizes, edge counts, and exact reference objectives;
- mean optimality ratio by solver family;
- feasibility rate for Minimum Vertex Cover;
- best and worst case-by-solver combinations;
- QAOA depth aggregate values;
- VQE ansatz/depth aggregate values;
- backend mean expectation energy, objective quality, and runtime;
- QAOA initialization aggregate expectation energy by depth;
- landscape best grid point and best expectation energy;
- mean and distribution of QAOA/VQE gradient norms.

## Remaining Interpretation Caveats

The benchmark suite is ready for local final-report execution, but the following caveats should remain
explicit in the report:

- all problem sizes are small enough for exact references;
- no claim of quantum speedup should be made;
- shot-based results are finite samples from ideal probabilities, not hardware runs;
- noisy results are simulated Aer noise, not physical-device data;
- QAOA and VQE optimize expectation energy, while decoded quality uses the dominant basis state;
- Minimum Vertex Cover must be interpreted with feasibility and penalty values, not only cover size;
- optimizer success flags and solution quality are related but not identical.
