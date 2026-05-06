# Final Benchmark Session 20260506

This run set is intended to generate the local results used for the final research report.
It focuses only on the supported problem families: MaxCut and Minimum Vertex Cover.

## Output Root

Use one shared output folder for all commands:

```powershell
data/results/session-20260506
```

Each CLI command creates a timestamped run folder under that session directory.

## Preflight

```powershell
& ".\.venv\Scripts\python.exe" -m pytest
```

Expected baseline after the TSP cleanup and campaign metric fix:

```text
45 passed
```

## Main Statevector Campaign

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run-benchmark-campaign --config configs/experiments/final_report_benchmark_campaign.yaml --output-dir data/results/session-20260506
```

Purpose:

- compare brute force, OpenJij, QAOA, and VQE on shared QUBO encodings;
- cover MaxCut and Minimum Vertex Cover;
- include 4-, 6-, and 8-variable cases;
- include structured and Erdős-Rényi graphs;
- include a weighted MaxCut case;
- compare QAOA depth and initialization sensitivity inside the campaign;
- compare VQE ansatz family and depth.

Validated expansion:

- 8 problem cases
- 10 solver cases
- 152 total runs

## Backend Campaign

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run-benchmark-campaign --config configs/experiments/final_report_backend_campaign.yaml --output-dir data/results/session-20260506
```

Purpose:

- compare statevector, shot-based, and noisy backend behavior;
- include repeated finite-shot/noisy trials;
- keep noisy simulation limited to small 4- and 6-variable cases.

Validated expansion:

- 3 problem cases
- 7 solver cases
- 39 total runs

## QAOA Initialization Study

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli compare-initializations --config configs/experiments/final_report_qaoa_initialization_comparison.yaml --output-dir data/results/session-20260506
```

Purpose:

- compare interpolation, warm-start, and random QAOA initialization;
- evaluate depths `p = 1, 2, 3`;
- use a 6-node Erdős-Rényi MaxCut instance instead of the trivial 4-cycle.

Validated expansion:

- 18 total QAOA runs

## Landscape And Gradient Study

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli analyze-landscape --config configs/experiments/final_report_landscape_analysis.yaml --output-dir data/results/session-20260506
```

Purpose:

- generate a QAOA `p=1` landscape heatmap;
- run QAOA multi-start convergence;
- collect finite-difference gradient statistics for QAOA and VQE.

Validated scope:

- 961 QAOA landscape grid points
- 6 QAOA multi-start runs
- 12 QAOA gradient samples
- 12 VQE gradient samples

## Interpretation Notes

Campaign `optimality_ratio` is now feasibility-adjusted. This prevents infeasible Minimum Vertex Cover
solutions from appearing strong only because they select fewer vertices. The raw objective-only ratio is
still logged as `objective_optimality_ratio` for diagnosis.

QAOA and VQE optimize expectation energy, while decoded solution quality is based on the dominant basis
state returned by the optimized circuit. Report expectation-energy trends and decoded objective quality as
related but distinct quantities.
