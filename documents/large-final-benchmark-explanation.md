# Large Final Benchmark Explanation

This document explains the proposed large final benchmark suite for the final research report.
It is designed as a heavier follow-up to the first final benchmark run under
`data/results/session-20260506/`.

The purpose is not to replace the first benchmark.
The purpose is to produce more informative and more statistically useful evidence after the first run
showed that the project executes very quickly on the local desktop.

The large suite should generate report-ready evidence under a new session folder, for example:

```text
data/results/session-20260506-large/
```

The project scope remains:

- QUBO modeling for MaxCut and Minimum Vertex Cover;
- QUBO-to-Ising conversion for QAOA and VQE;
- exact brute-force references for all selected instances;
- OpenJij simulated annealing as a classical stochastic sampler;
- QAOA and VQE comparisons on shared QUBO/Ising encodings;
- backend comparison under statevector, finite-shot, and noisy simulation;
- initialization, depth, ansatz, landscape, and gradient analysis.

Traveling Salesman Problem experiments remain out of scope.
The codebase currently exposes `MaxCutInstance` and `MinimumVertexCoverInstance` from the problem package.

## Why A Larger Benchmark Is Needed

The first final benchmark was useful because it proved that the full pipeline works:
problem generation, QUBO construction, Ising conversion, solver execution, artifact logging,
aggregation, plotting, and discussion.

However, the first run was intentionally small.
It used a small number of graph instances and only a few stochastic repetitions.
That was enough for pipeline validation, but not enough for stronger discussion of trends.

The first result discussion suggests several reasons to scale up:

- simple cycle cases were solved by almost every method;
- weighted 8-variable MaxCut was more informative than unweighted cycle cases;
- 8-variable Minimum Vertex Cover on Erdős-Rényi graphs was also a useful stress case;
- QAOA interpolation was not always robust on constrained MVC cases;
- optimizer status and decoded solution quality often diverged;
- OpenJij should be tested with more trials before interpreting sampler behavior;
- backend noise did not degrade decoded quality on the tiny backend cases, so harder backend cases are needed;
- the landscape and gradient study was useful, but it used only one small MaxCut instance.

The large benchmark therefore scales in three careful ways:

1. more graph instances and more random seeds;
2. moderate variable sizes up to `n = 12`, while keeping exact references cheap;
3. deeper QAOA/VQE settings, but still within local statevector limits.

This is still a course-scale benchmark.
It should not be presented as evidence of quantum advantage.
Its value is stronger empirical coverage and better final-report discussion.

## General Large Report Strategy

Use the large benchmark as the main final-report evidence if it completes cleanly.
Use the first final benchmark as a backup and sanity check.

The most useful final-report structure is:

- use the large main campaign for solver-family, problem-family, size, random-seed, QAOA-depth, and VQE-ansatz tables;
- use the large backend campaign for expectation-energy and runtime degradation under finite-shot/noisy modes;
- use the large QAOA initialization study for MaxCut vs MVC initialization behavior;
- use the large landscape study for trainability and objective-landscape discussion;
- use selected per-run artifacts as concrete examples of QUBO matrices, Ising Hamiltonians, decoded bitstrings, and feasibility checks.

The report should emphasize repeated-instance trends rather than single-instance anecdotes.
Single-run artifacts should be used only as examples.

## Run Order

Recommended order:

1. preflight validation;
2. optional smoke run on a very small subset;
3. large main statevector campaign;
4. large backend campaign;
5. large QAOA initialization study;
6. large landscape and gradient study;
7. optional hard-case extension if time remains.

If any campaign becomes unexpectedly slow, prioritize the large main statevector campaign first.
That campaign gives the most useful tables for the final report.

## Preflight Validation

Command:

```powershell
& ".\.venv\Scripts\python.exe" -m pytest
```

Purpose:

The preflight confirms that imports, config loading, solvers, campaign aggregation,
plotting, and artifact-writing workflows are still internally consistent.

Expected result:

```text
all tests passed
```

The earlier expected count was:

```text
45 passed
```

If new tests were added, the exact count may be larger.
The important point is that the full test suite should pass before running the large benchmark.

Artifacts to keep:

- terminal output showing the passing test count;
- Python version;
- package versions if easily available;
- git commit hash if the repository is under version control.

Remarks:

This is not experimental evidence.
It is reproducibility evidence.
Do not run the large benchmark if the test suite fails.

## Optional Smoke Run

Config:

```text
configs/experiments/large_final_report_smoke_campaign.yaml
```

Command:

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run-benchmark-campaign --config configs/experiments/large_final_report_smoke_campaign.yaml --output-dir data/results/session-20260506-large
```

Purpose:

The smoke run checks that the large campaign schema is valid before launching the full run.
It should use only a few cases and a few solvers.

Included problem cases:

- MaxCut cycle with 4 variables;
- weighted MaxCut Erdős-Rényi graph with 8 variables;
- Minimum Vertex Cover Erdős-Rényi graph with 8 variables.

Included solver cases:

- brute force exact reference;
- OpenJij simulated annealing with two trials;
- QAOA interpolation at `p = 1`;
- QAOA random at `p = 2` with two seeds;
- VQE problem-aware ansatz at depth 1 with two seeds;
- VQE hardware-efficient ansatz at depth 1 with two seeds.

Target scope:

- 3 problem cases;
- around 27 runs, depending on exact seed expansion;
- exact references available for all cases.

Expected result:

The smoke run should complete quickly and produce the normal artifact structure.
If the smoke run fails, fix the config before running the large campaign.

## Large Main Statevector Campaign

Config:

```text
configs/experiments/large_final_report_benchmark_campaign.yaml
```

Command:

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run-benchmark-campaign --config configs/experiments/large_final_report_benchmark_campaign.yaml --output-dir data/results/session-20260506-large
```

Purpose:

This is the main large final-report benchmark.
It compares solver families on many shared QUBO encodings while keeping all quantum runs statevector-based.
This isolates modeling, depth, initialization, ansatz, and optimizer effects from shot noise and simulated device noise.

This campaign is larger than the first final benchmark in four ways:

- more graph sizes;
- more random graph seeds;
- more OpenJij trials;
- higher QAOA and VQE depths.

### Included Problem Cases

MaxCut cases:

- MaxCut cycle with 4 variables;
- MaxCut cycle with 6 variables;
- MaxCut cycle with 8 variables;
- MaxCut cycle with 10 variables;
- MaxCut cycle with 12 variables;
- MaxCut Erdős-Rényi graph with 8 variables, seed `11`;
- MaxCut Erdős-Rényi graph with 8 variables, seed `17`;
- MaxCut Erdős-Rényi graph with 10 variables, seed `11`;
- MaxCut Erdős-Rényi graph with 10 variables, seed `17`;
- MaxCut Erdős-Rényi graph with 12 variables, seed `11`;
- MaxCut Erdős-Rényi graph with 12 variables, seed `17`;
- weighted MaxCut Erdős-Rényi graph with 8 variables, seed `17`;
- weighted MaxCut Erdős-Rényi graph with 8 variables, seed `23`;
- weighted MaxCut Erdős-Rényi graph with 10 variables, seed `17`;
- weighted MaxCut Erdős-Rényi graph with 10 variables, seed `23`;
- weighted MaxCut Erdős-Rényi graph with 12 variables, seed `17`;
- weighted MaxCut Erdős-Rényi graph with 12 variables, seed `23`.

Minimum Vertex Cover cases:

- Minimum Vertex Cover path with 4 variables;
- Minimum Vertex Cover cycle with 6 variables;
- Minimum Vertex Cover path with 8 variables;
- Minimum Vertex Cover cycle with 8 variables;
- Minimum Vertex Cover path with 10 variables;
- Minimum Vertex Cover cycle with 10 variables;
- Minimum Vertex Cover path with 12 variables;
- Minimum Vertex Cover cycle with 12 variables;
- Minimum Vertex Cover Erdős-Rényi graph with 8 variables, seed `11`;
- Minimum Vertex Cover Erdős-Rényi graph with 8 variables, seed `17`;
- Minimum Vertex Cover Erdős-Rényi graph with 10 variables, seed `11`;
- Minimum Vertex Cover Erdős-Rényi graph with 10 variables, seed `17`;
- Minimum Vertex Cover Erdős-Rényi graph with 12 variables, seed `11`;
- Minimum Vertex Cover Erdős-Rényi graph with 12 variables, seed `17`.

Target problem scope:

- 17 MaxCut cases;
- 14 Minimum Vertex Cover cases;
- 31 total problem cases;
- maximum variable count `n = 12`;
- exact reference search space at most `2^12 = 4096` bitstrings per case.

### Included Solver Cases

Classical references and samplers:

- brute force exact reference;
- OpenJij simulated annealing with 10 independent trials per problem case.

QAOA statevector cases:

- QAOA interpolation initialization at `p = 1`;
- QAOA interpolation initialization at `p = 2`;
- QAOA interpolation initialization at `p = 3`;
- QAOA interpolation initialization at `p = 4`;
- QAOA random initialization at `p = 1`, repeated across 5 seeds;
- QAOA random initialization at `p = 2`, repeated across 5 seeds;
- QAOA random initialization at `p = 3`, repeated across 5 seeds;
- QAOA random initialization at `p = 4`, repeated across 5 seeds.

VQE statevector cases:

- VQE problem-aware ansatz at depth 1, repeated across 4 seeds;
- VQE problem-aware ansatz at depth 2, repeated across 4 seeds;
- VQE problem-aware ansatz at depth 3, repeated across 4 seeds;
- VQE hardware-efficient ansatz at depth 1, repeated across 4 seeds;
- VQE hardware-efficient ansatz at depth 2, repeated across 4 seeds;
- VQE hardware-efficient ansatz at depth 3, repeated across 4 seeds.

Recommended optimization settings:

- keep optimizer as COBYLA for continuity with the first benchmark;
- increase QAOA maximum evaluations relative to the first benchmark;
- use a QAOA max-iteration cap around `220` to `300`;
- use a VQE max-iteration cap around `220` to `300`;
- log optimizer termination message, success flag, final expectation energy, evaluation count, and decoded solution quality separately.

Target run count:

- per problem case:
  - 1 brute-force run;
  - 10 OpenJij runs;
  - 4 QAOA interpolation runs;
  - 20 QAOA random-start runs;
  - 12 VQE problem-aware runs;
  - 12 VQE hardware-efficient runs;
  - 59 total runs per problem case.
- with 31 problem cases:
  - about 1829 total solver runs.

The exact count may differ if the config system expands seeds differently.
Check the generated `summary.json` after execution.

### Expected Theoretical Results and Remarks

Brute force should return the exact optimum for every case.
It remains a reference method, not a scalable method.

OpenJij should become easier to interpret than in the first benchmark because each problem has 10 trials.
This makes sampler variance more visible.
It also reduces the risk of overinterpreting one unlucky trial.

Cycle and path cases are validation and scaling cases.
They should often be easier than random and weighted cases.
They are still useful because they show whether algorithms behave consistently as `n` grows.

Weighted MaxCut Erdős-Rényi cases should be among the most informative MaxCut cases.
The first final benchmark already showed that weighted 8-variable MaxCut was harder than simple cycles.
The large campaign checks whether that remains true across more seeds and sizes.

MVC Erdős-Rényi cases should be among the most informative constrained cases.
They test both objective quality and feasibility.
For MVC, `optimality_ratio`, `objective_optimality_ratio`, feasibility, penalty value, and cover size should all be interpreted together.

QAOA depth should generally improve expectation-energy quality as depth increases.
However, decoded dominant-bitstring quality may not improve monotonically.
This is especially important for MVC because penalty constraints can create infeasible dominant outputs.

QAOA random initialization should be compared against interpolation for every problem family.
The first benchmark suggested that interpolation can fail on constrained MVC cases.
The large benchmark should test whether this was a single-instance artifact or a repeated pattern.

VQE depth 3 may improve expressivity.
It may also make optimization harder because the parameter space is larger.
For that reason, optimizer success should not be treated as equivalent to decoded solution quality.

Problem-aware VQE is expected to remain stronger than hardware-efficient VQE on some MVC cases.
The large benchmark should test whether this persists across several random seeds.

### Artifacts To Save For The Report

Save the normal campaign artifacts:

- `summary.json`;
- `notes.md`;
- `tables/run_metrics.csv`;
- `tables/case_aggregates.csv`;
- `tables/solver_family_aggregates.csv`;
- `tables/problem_family_aggregates.csv`;
- `tables/problem_size_aggregates.csv`;
- `tables/qaoa_depth_aggregates.csv`;
- `tables/vqe_depth_aggregates.csv`;
- `plots/optimality_ratio_by_case.png`;
- `plots/runtime_by_case.png`;
- `plots/optimality_ratio_by_solver_family.png`;
- `plots/optimality_ratio_by_problem_family.png`.

Also save selected per-run artifacts:

- one MaxCut cycle QUBO example;
- one weighted MaxCut QUBO example;
- one MVC QUBO example with penalty terms;
- one QUBO-to-Ising conversion example;
- one QAOA trace from a successful run;
- one QAOA trace from a low-quality or infeasible decoded run;
- one VQE trace where optimizer success and decoded quality diverge.

### Best Report Uses

Use this campaign for:

- the primary solver-family comparison table;
- MaxCut vs MVC comparison;
- weighted vs unweighted MaxCut discussion;
- path/cycle vs random graph discussion;
- size trend from 4 to 12 variables;
- QAOA depth comparison from `p = 1` to `p = 4`;
- QAOA interpolation vs random initialization comparison;
- VQE problem-aware vs hardware-efficient ansatz comparison;
- VQE depth comparison from depth 1 to depth 3;
- feasibility-aware discussion for MVC;
- runtime and evaluation-count discussion.

## Large Backend Campaign

Config:

```text
configs/experiments/large_final_report_backend_campaign.yaml
```

Command:

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run-benchmark-campaign --config configs/experiments/large_final_report_backend_campaign.yaml --output-dir data/results/session-20260506-large
```

Purpose:

This campaign studies how backend execution mode affects QAOA and VQE behavior.
It is larger than the first backend campaign, but still smaller than the main statevector campaign.
Noisy simulation is more expensive, so this campaign should focus on representative hard cases.

### Included Problem Cases

Recommended cases:

- MaxCut cycle with 6 variables;
- MaxCut Erdős-Rényi graph with 8 variables, seed `11`;
- weighted MaxCut Erdős-Rényi graph with 8 variables, seed `17`;
- weighted MaxCut Erdős-Rényi graph with 10 variables, seed `17`;
- Minimum Vertex Cover cycle with 6 variables;
- Minimum Vertex Cover Erdős-Rényi graph with 8 variables, seed `11`;
- Minimum Vertex Cover Erdős-Rényi graph with 10 variables, seed `11`.

Target scope:

- 7 problem cases;
- includes validation, random, weighted, and constrained cases;
- maximum variable count `n = 10` for backend runs.

### Included Solver and Backend Cases

For each problem case:

- brute force reference;
- QAOA statevector at `p = 2`, repeated across 2 seeds;
- QAOA finite-shot sampling at `1024` shots, repeated across 2 seeds;
- QAOA finite-shot sampling at `4096` shots, repeated across 2 seeds;
- QAOA noisy sampling with `depolarizing_readout` at `1024` shots, repeated across 2 seeds;
- QAOA noisy sampling with `depolarizing_readout` at `4096` shots, repeated across 2 seeds;
- VQE problem-aware statevector at depth 2, repeated across 2 seeds;
- VQE problem-aware finite-shot sampling at `1024` shots, repeated across 2 seeds;
- VQE problem-aware finite-shot sampling at `4096` shots, repeated across 2 seeds;
- VQE problem-aware noisy sampling with `depolarizing_readout` at `1024` shots, repeated across 2 seeds;
- VQE problem-aware noisy sampling with `depolarizing_readout` at `4096` shots, repeated across 2 seeds.

Target run count:

- 1 brute-force run per problem case;
- 10 QAOA backend runs per problem case;
- 10 VQE backend runs per problem case;
- 21 total runs per problem case;
- around 147 total runs for 7 problem cases.

### Expected Theoretical Results and Remarks

Statevector mode is the clean deterministic reference for the selected variational algorithm path.

Shot-based mode should show finite-sampling variation.
Using both `1024` and `4096` shots allows a discussion of shot-count sensitivity.

Noisy mode should usually increase runtime.
It may also degrade expectation energy.
Decoded objective quality may still remain high on small cases, so expectation energy and dominant-bitstring probability should be reported separately.

The first backend campaign did not show decoded-quality degradation under noise because the cases were very small.
This larger backend campaign includes harder 8-variable and 10-variable cases so that backend effects have a better chance to appear.

Shot-based results should still be described carefully.
They are finite samples from ideal probabilities.
They are not hardware noise.

Noisy results should be described as simulated Aer noise.
They are not evidence from a physical quantum device.

### Artifacts To Save For The Report

- `summary.json`;
- `notes.md`;
- `tables/run_metrics.csv`;
- `tables/backend_aggregates.csv`;
- backend aggregate plots;
- expectation-energy by backend plot;
- runtime by backend plot;
- dominant-bitstring probability by backend plot, if available;
- selected `result.json` files showing backend metadata, shot count, seed, and noise model;
- selected traces comparing statevector, finite-shot, and noisy behavior on the same problem case.

### Best Report Uses

Use this campaign for:

- backend comparison table;
- finite-shot vs statevector discussion;
- shot-count sensitivity discussion;
- simulated-noise runtime discussion;
- expectation-energy degradation discussion;
- distinction between expectation quality and decoded bitstring quality;
- limitations statement about simulated backends.

## Large QAOA Initialization Study

Config:

```text
configs/experiments/large_final_report_qaoa_initialization_comparison.yaml
```

Command:

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli compare-initializations --config configs/experiments/large_final_report_qaoa_initialization_comparison.yaml --output-dir data/results/session-20260506-large
```

Purpose:

This workflow isolates QAOA initialization effects across several problem types.
The first initialization study used one 6-variable MaxCut case.
The large version should test whether the same conclusions hold on weighted and constrained cases.

### Included Problem Cases

Recommended cases:

- MaxCut Erdős-Rényi graph with 8 variables, seed `11`;
- weighted MaxCut Erdős-Rényi graph with 8 variables, seed `17`;
- weighted MaxCut Erdős-Rényi graph with 10 variables, seed `17`;
- Minimum Vertex Cover Erdős-Rényi graph with 8 variables, seed `11`;
- Minimum Vertex Cover Erdős-Rényi graph with 10 variables, seed `11`.

If the current CLI supports only one problem per initialization config, create one config file per case:

```text
configs/experiments/large_final_report_qaoa_init_maxcut_er8_seed11.yaml
configs/experiments/large_final_report_qaoa_init_maxcut_weighted_er8_seed17.yaml
configs/experiments/large_final_report_qaoa_init_maxcut_weighted_er10_seed17.yaml
configs/experiments/large_final_report_qaoa_init_mvc_er8_seed11.yaml
configs/experiments/large_final_report_qaoa_init_mvc_er10_seed11.yaml
```

### Included Experiments

For each selected problem case:

- interpolation initialization at `p = 1`, `p = 2`, `p = 3`, `p = 4`, and `p = 5`;
- warm-start initialization from lower-depth optimized parameters through `p = 5`;
- random initialization at `p = 1` through `p = 5`, with 8 random trials per depth.

Target run count per problem case:

- 5 interpolation runs;
- 5 warm-start runs;
- 40 random-start runs;
- 50 total QAOA runs per problem case.

Target total scope:

- 5 problem cases;
- about 250 total QAOA runs.

### Expected Theoretical Results and Remarks

Increasing QAOA depth should often improve best expectation energy.
This may not imply monotonic decoded objective quality.

Warm-start should often be more stable at higher depth because it reuses lower-depth optimized parameters.
The large study should test whether this remains true beyond the original 6-variable MaxCut example.

Random starts should expose local-minimum and optimizer-sensitivity behavior.
The larger number of random trials makes this more meaningful than the first run.

Initialization behavior may differ between MaxCut and MVC.
MVC includes penalty constraints, so an initialization that works well for MaxCut may still produce infeasible dominant bitstrings for MVC.

Optimizer success flags should be interpreted separately from decoded quality.
This is especially important at `p = 4` and `p = 5`, where the optimizer may hit iteration caps while still producing good bitstrings.

### Artifacts To Save For The Report

- `summary.json` for each initialization config;
- `tables/run_metrics.csv`;
- `tables/aggregate_metrics.csv`;
- approximation ratio vs depth plots;
- best expectation energy vs depth plots;
- runtime vs depth plots;
- evaluation count vs depth plots;
- parameter-value plots by initialization strategy;
- per-run trace JSON files.

### Best Report Uses

Use this study for:

- QAOA initialization strategy comparison;
- depth-vs-expectation discussion;
- random-start variance discussion;
- warm-start discussion;
- MaxCut vs MVC initialization transfer discussion;
- explanation of why optimizer success is not the same thing as final decoded quality.

## Large Landscape And Gradient Study

Config:

```text
configs/experiments/large_final_report_landscape_analysis.yaml
```

Command:

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli analyze-landscape --config configs/experiments/large_final_report_landscape_analysis.yaml --output-dir data/results/session-20260506-large
```

Purpose:

This workflow produces visual and numeric evidence about optimization landscapes.
The first landscape study focused on one 6-variable MaxCut case.
The large version should include both MaxCut and MVC cases and should increase the number of gradient samples.

### Included Problem Cases

Recommended cases:

- MaxCut Erdős-Rényi graph with 8 variables, seed `11`;
- weighted MaxCut Erdős-Rényi graph with 8 variables, seed `17`;
- Minimum Vertex Cover Erdős-Rényi graph with 8 variables, seed `11`;
- Minimum Vertex Cover cycle with 8 variables.

### Included Experiments

QAOA landscape scans:

- QAOA `p = 1` dense grid scan over `gamma` and `beta`;
- recommended grid resolution: `61 x 61`;
- 3721 grid points per problem case;
- 14884 total grid points across 4 problem cases.

QAOA multi-start optimization:

- QAOA `p = 1` multi-start optimization from 20 random starts per problem case;
- QAOA `p = 2` multi-start optimization from 20 random starts per problem case, if the workflow supports this;
- if `p = 2` multi-start is not supported, keep the `p = 1` multi-start results and increase random starts to 40.

Gradient sampling:

- finite-difference QAOA gradient samples at `p = 1`;
- finite-difference QAOA gradient samples at `p = 2`, if supported;
- finite-difference VQE gradient samples for hardware-efficient depth 1;
- finite-difference VQE gradient samples for hardware-efficient depth 2;
- recommended sample count: 50 random parameter points per method and problem case.

### Expected Theoretical Results and Remarks

The QAOA `p = 1` energy landscape should show structured periodic behavior.
The dominant decoded objective may be piecewise constant even when expectation energy changes smoothly.

Weighted MaxCut should have a more informative landscape than simple cycles.
The weighted objective can create sharper distinctions between high-quality and low-quality regions.

MVC landscapes should be interpreted with feasibility.
A low raw objective value is not useful if the decoded bitstring violates cover constraints.

Gradient statistics should not be used to claim a barren plateau.
The selected sizes are still small.
The study is a trainability snapshot, not a scaling proof.

VQE gradient norms may differ strongly between depth 1 and depth 2 because the parameter count and ansatz expressivity change.

### Artifacts To Save For The Report

- `tables/qaoa_p1_landscape.csv` for each problem case;
- `tables/qaoa_multistart_runs.csv`;
- `tables/qaoa_gradient_statistics.csv`;
- `tables/vqe_gradient_statistics.csv`;
- `summary.json`;
- `plots/qaoa_p1_landscape_energy.png`;
- `plots/qaoa_p1_landscape_objective.png`;
- `plots/qaoa_p1_landscape_feasibility.png`, if available for MVC;
- `plots/qaoa_multistart_convergence.png`;
- `plots/qaoa_gradient_norms.png`;
- `plots/vqe_gradient_norms.png`;
- selected trace JSON files under `traces/`.

### Best Report Uses

Use this study for:

- QAOA heatmap figures;
- smooth expectation landscape vs discrete decoded objective discussion;
- constrained feasibility landscape discussion for MVC;
- multi-start convergence figure;
- QAOA vs VQE gradient norm comparison;
- small-scale trainability discussion.

## Optional Hard-Case Extension

Config:

```text
configs/experiments/large_final_report_hard_case_extension.yaml
```

Command:

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run-benchmark-campaign --config configs/experiments/large_final_report_hard_case_extension.yaml --output-dir data/results/session-20260506-large
```

Purpose:

This optional extension focuses only on cases that were hard in the first benchmark or are expected to be hard in the large benchmark.
Run this only after the main large campaign finishes.

### Candidate Problem Cases

- weighted MaxCut Erdős-Rényi graph with 8 variables, seed `17`;
- weighted MaxCut Erdős-Rényi graph with 10 variables, seed `17`;
- weighted MaxCut Erdős-Rényi graph with 12 variables, seed `17`;
- Minimum Vertex Cover Erdős-Rényi graph with 8 variables, seed `17`;
- Minimum Vertex Cover Erdős-Rényi graph with 10 variables, seed `17`;
- Minimum Vertex Cover Erdős-Rényi graph with 12 variables, seed `17`.

### Candidate Solver Cases

- brute force exact reference;
- OpenJij with 30 independent trials;
- QAOA interpolation from `p = 1` to `p = 5`;
- QAOA random from `p = 1` to `p = 5`, with 10 seeds per depth;
- VQE problem-aware ansatz depth 1 to 4, with 6 seeds per depth;
- VQE hardware-efficient ansatz depth 1 to 4, with 6 seeds per depth.

### Best Report Uses

Use this extension only if it reveals clear additional information.
Do not overload the final report with too many tables.
Possible uses:

- hard-case comparison table;
- best-vs-mean solver behavior;
- failure-mode examples;
- optimizer cap discussion;
- feasibility failure discussion for MVC.

## Cross-Campaign Values To Extract

After all large campaigns finish, extract these values for the final report:

- test pass count;
- Python version;
- package versions;
- total number of runs per campaign;
- total wall-clock runtime per campaign;
- problem labels, graph sizes, edge counts, graph family, and exact objectives;
- exact QUBO energy for every problem case;
- mean optimality ratio by solver family;
- median optimality ratio by solver family;
- best and worst case-by-solver combinations;
- feasibility rate for MVC;
- objective-only optimality ratio for MVC;
- OpenJij best, mean, and variance across trials;
- QAOA depth aggregates from `p = 1` to `p = 4`;
- QAOA initialization aggregates by strategy;
- VQE ansatz/depth aggregates;
- optimizer success rate by method and depth;
- solution quality success rate by method and depth;
- evaluation count by method and depth;
- backend expectation energy by mode;
- backend runtime by mode;
- shot-count sensitivity between `1024` and `4096` shots;
- noisy vs noiseless expectation-energy difference;
- landscape best grid point per problem case;
- distribution of decoded objectives over landscape grid points;
- mean and distribution of QAOA gradient norms;
- mean and distribution of VQE gradient norms.

## Suggested Final Report Tables

Primary tables:

- solver-family aggregate table;
- problem-family aggregate table;
- problem-size aggregate table;
- QAOA depth aggregate table;
- QAOA initialization aggregate table;
- VQE ansatz/depth aggregate table;
- backend aggregate table;
- selected hard-case table.

Secondary tables:

- exact reference table for all problem cases;
- OpenJij trial summary table;
- optimizer-status vs decoded-quality table;
- MVC feasibility table;
- gradient statistics table.

Do not include every per-run row in the final report body.
Keep full CSV files as reproducibility artifacts.

## Suggested Final Report Figures

Primary figures:

- optimality ratio by problem case;
- optimality ratio by solver family;
- runtime by problem case;
- QAOA mean optimality or expectation energy vs depth;
- VQE mean optimality or expectation energy by ansatz/depth;
- backend expectation energy by mode;
- backend runtime by mode;
- QAOA landscape energy heatmap;
- QAOA multi-start convergence plot;
- QAOA and VQE gradient norm plots.

Optional figures:

- feasibility rate by MVC problem case;
- OpenJij best-vs-mean plot;
- shot-count comparison plot;
- optimizer success vs solution quality scatter plot.

## Practical Local-Safety Notes

The recommended maximum variable count is `n = 12`.
This keeps exact brute-force references cheap because the full bitstring space has only `4096` states.

Statevector memory should remain manageable at `n = 12`.
The main cost will be repeated optimizer evaluations, not storing the statevector.

Noisy simulation is more expensive than statevector simulation.
For this reason, the backend campaign uses fewer problem cases and stops at `n = 10`.

If the large benchmark becomes slower than expected, reduce in this order:

1. remove VQE depth 3 from the main campaign;
2. reduce QAOA random seeds from 5 to 3;
3. reduce OpenJij trials from 10 to 5;
4. remove `n = 12` MVC Erdős-Rényi cases;
5. remove noisy `4096`-shot backend cases;
6. keep the weighted MaxCut and MVC random cases as the highest-priority stress cases.

Do not reduce the exact brute-force references.
They are essential for interpreting optimality ratios.

## Interpretation Caveats

The large benchmark still uses small exact-reference instances.
No quantum advantage claim should be made.

Brute force will likely remain fastest for these sizes.
That is expected and should be stated clearly.

Statevector results are ideal simulator results.
They do not represent hardware execution.

Shot-based results are finite samples from ideal probabilities.
They should not be described as hardware-noisy results.

Noisy results are simulated noise results.
They should not be described as real-device evidence.

QAOA and VQE optimize expectation energy.
The final reported solution quality is based on decoded bitstrings.
These are related but not identical.

For MVC, feasibility must be discussed explicitly.
A decoded bitstring with a small cover size is not a valid solution if it violates edge-cover constraints.

Optimizer success flags are useful diagnostics.
They are not the same as solution quality.
A run can report optimizer failure and still decode a good bitstring.
A run can report optimizer success and still decode an infeasible or low-quality bitstring.

Large repeated experiments provide stronger empirical trends than the first benchmark.
They still do not prove general behavior for all QUBO instances.

## Minimal Version If Time Is Limited

If there is not enough time to run the full large suite, run this reduced version:

Main campaign:

- keep all 31 problem cases;
- brute force;
- OpenJij with 5 trials;
- QAOA interpolation `p = 1` to `p = 3`;
- QAOA random `p = 1` to `p = 3` with 3 seeds;
- VQE problem-aware depth 1 and 2 with 3 seeds;
- VQE hardware-efficient depth 1 and 2 with 3 seeds.

Backend campaign:

- keep only 5 problem cases;
- use `1024` shots only;
- keep statevector, shot-based, and noisy modes.

Initialization study:

- use 3 problem cases;
- depths `p = 1` to `p = 4`;
- 5 random trials per depth.

Landscape study:

- use 2 problem cases;
- `41 x 41` QAOA `p = 1` grid;
- 25 gradient samples per method.

This reduced version is still stronger than the first final benchmark because it includes more problem instances and more repeated seeds.

## Final Recommendation

The recommended large benchmark is:

- 31 problem cases in the main statevector campaign;
- QAOA depths up to `p = 4`;
- VQE depths up to 3;
- OpenJij with 10 trials;
- backend comparison on 7 representative cases;
- QAOA initialization study on 5 representative cases;
- landscape and gradient study on 4 representative cases.

This design is broad enough for a thorough final-report discussion.
It is still light enough to remain local-desktop friendly.
It also directly responds to the first benchmark results by adding more random instances,
more stochastic repetitions, harder weighted/random cases, deeper variational circuits,
and better backend/landscape evidence.
