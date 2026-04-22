# QUBO Modeling and Variational Quantum Optimization for Small MaxCut and Minimum Vertex Cover Benchmarks

## Project Objectives and Scope

The repository goals were to:

1. implement transparent QUBO encodings for benchmark problems;
2. preserve exact classical references on small instances;
3. support QAOA and VQE on the same encoded problems;
4. compare solver families and backend modes through shared experiment schemas; and
5. support first-pass trainability and landscape analysis.


## Software and Code Architecture

The codebase is organized as a modular Python package under `src/qubo_vqa/`. The key architectural decision is to keep QUBO as the canonical internal boundary. Problem modules encode instances into `QUBOModel`, classical solvers consume the QUBO directly, and quantum workflows convert the QUBO into `IsingModel` when constructing or evaluating quantum costs.

The main modules are:

- `core/` for QUBO, Ising, and solver-result data structures;
- `problems/` for MaxCut and Minimum Vertex Cover encoders and decoders;
- `solvers/classical/` for brute force and OpenJij;
- `solvers/quantum/` for QAOA, VQE, backend handling, ansatz construction, and initialization;
- `experiments/` for the CLI-connected execution workflows;
- `analysis/` for metrics, plots, campaign summaries, landscape tools, and gradient statistics.

The main user entry point is `python -m qubo_vqa.cli`. Config-driven execution. YAML files in `configs/experiments/` define problems, solver settings, output tags, comparisons, and campaigns. Every executed run writes structured artifacts such as `config.json`, `result.json`, `metrics.json`, `trace.json`, plots, and aggregate summaries.

## Experimental Methodology

### Environment and validation

The project was run with the repository virtual environment and Python `3.12.10`. The full test suite was executed first:

```text
44 passed
```

### Executed experiments

The executed command set covered:

- single-run classical MaxCut and Minimum Vertex Cover;
- single-run QAOA and VQE for both benchmark families;
- MaxCut solver comparison across brute force, OpenJij, QAOA, and VQE;
- QAOA backend comparison across statevector, shot-based, and noisy modes;
- QAOA initialization comparison over depths 1 and 2;
- QAOA landscape analysis with multi-start and gradient statistics;
- starter, moderate, and backend-focused benchmark campaigns.

All outputs from this session were written under `data/results/session-20260415/`.

## Results

### Representative single-run validations

The single-run workflows confirmed that the full vertical slices were operational for both problem families.

| Run | Key observed result |
| --- | --- |
| Classical MaxCut | objective `4.0`, feasible, runtime `0.0006 s` |
| Classical MVC | objective `2.0`, feasible, runtime `0.0006 s` |
| QAOA MaxCut statevector | objective `4.0`, best expectation `-2.9999981`, `35` evaluations, runtime `0.4014 s` |
| VQE MaxCut statevector | objective `4.0`, best expectation `-2.9999998`, `70` evaluations, runtime `0.3949 s` |
| QAOA MVC statevector | objective `2.0`, feasible, best expectation `3.8094`, runtime `0.3917 s` |
| VQE MVC statevector | objective `2.0`, feasible, best expectation `2.0000000`, runtime `0.4279 s` |

These runs show that both benchmark families can be encoded, solved, decoded, and logged through the same pipeline.

### MaxCut solver comparison

The dedicated solver-comparison workflow compared the four main solver families on the same 4-node MaxCut cycle. All four achieved the optimal decoded objective value `4.0` and approximation ratio `1.0`.

| Solver | Mean runtime (s) | Evaluations | Objective |
| --- | ---: | ---: | ---: |
| Brute force | `0.0005` | `16` | `4.0` |
| OpenJij | `0.1376` | `64` reads | `4.0` |
| QAOA | `0.3447` | `35` | `4.0` |
| VQE | `0.0363` | `70` | `4.0` |

On this smallest preserved instance, the solver families were indistinguishable in decoded solution quality. The main differences were in evaluation behavior and runtime.

### QAOA backend comparison

The backend-comparison workflow kept the same QAOA problem and optimizer settings while changing only the backend mode. The decoded MaxCut solution stayed optimal in all three cases, but the expectation values and runtime changed.

| Backend | Best expectation energy | Runtime (s) | Objective |
| --- | ---: | ---: | ---: |
| Statevector | `-2.9999981` | `0.3641` | `4.0` |
| Shot-based (`2048` shots) | `-3.0126953` | `0.0137` | `4.0` |
| Noisy (`2048` shots, `depolarizing_readout`) | `-2.8613281` | `1.3909` | `4.0` |

The main qualitative observation is that the noisy backend degraded the expectation value and increased runtime relative to the other two modes, while the decoded optimum remained stable on this very small benchmark.

### QAOA initialization comparison

The initialization workflow compared `interpolation`, `warm_start`, and `random` strategies at QAOA depths `p=1` and `p=2`. All executed runs still recovered the optimal decoded MaxCut objective `4.0`, but the best expectation values differed strongly at depth `2`.

At `p=1`, all strategies were effectively equivalent on this small cycle and produced expectation energies near `-3.0`. At `p=2`, the strongest expectation value came from warm start:

- `warm_start`, `p=2`: mean best expectation `-3.9992312`
- `interpolation`, `p=2`: mean best expectation `-3.3518641`
- `random`, `p=2`: mean best expectation `-3.0220253`

However, all three depth-2 strategy groups reported optimizer success rate `0.0` in the aggregate summary because the runs hit the configured COBYLA iteration cap. Need to investigate and fix this behaviour/problem.

### Landscape analysis

The preserved landscape workflow produced a QAOA `p=1` grid scan, multi-start traces, and gradient-statistics summaries.

Observed highlights:

- QAOA landscape grid points: `441`
- Best sampled point: `gamma = 0.7854`, `beta = 1.1781`
- Best QAOA expectation energy on grid: `-3.0`
- Multi-start runs: `4`
- Best decoded multi-start objective: `4.0`
- Mean QAOA gradient norm: `2.1205`
- Mean VQE gradient norm: `0.5977`

These results support two modest conclusions. First, the 4-cycle MaxCut instance remains easy enough that multiple QAOA starting points reach the optimal decoded solution. Second, the trainability summaries differ numerically between QAOA and the chosen VQE ansatz, but the study remains limited to one small instance and one shallow ansatz setting.

### Starter benchmark campaign

The starter campaign executed `12` runs across `2` problem cases and `6` solver cases. The aggregate notes show perfect decoded solution quality across the starter set:

- all runs had exact references;
- all runs had feasible decoded solutions;
- all runs achieved mean optimality ratio `1.0`.

Note: QAOA had optimizer success rate `1.0` on the starter slice, while VQE had optimizer success rate `0.0` even though its decoded solution quality remained perfect. Need to investigate and/or fix this behaviour/problem.

### Moderate benchmark campaign

The moderate campaign expanded the study to `48` runs across `6` problem cases and `8` solver cases. This is the broadest dataset executed in this session and the most informative aggregate result for the final discussion.

The notes indicate:

- MaxCut size `6`: mean optimality ratio `0.9688`
- Minimum Vertex Cover size `6`: mean optimality ratio `0.9906`
- QAOA statevector mean optimality ratio: `0.9972`
- VQE statevector mean optimality ratio: `0.9236`

The moderate campaign also exposed harder cases:

- `maxcut_erdos_renyi_6_seed11 / vqe_hardware_efficient_d1`: mean optimality ratio `0.6667`
- `mvc-path-4 / vqe_problem_aware_d1`: mean optimality ratio `0.6667`
- `mvc_cycle_6_seed11 / vqe_problem_aware_d1`: mean optimality ratio `0.7500`
- `maxcut_erdos_renyi_6_seed11 / qaoa_random_p1`: mean optimality ratio `0.8333`
- `mvc_erdos_renyi_6_seed11 / qaoa_interpolation_p2`: mean optimality ratio `0.6000`

This campaign therefore gives the clearest evidence that the repository is not merely solving trivial starter cases. Once the instances become slightly less structured, performance differences appear, especially for some VQE settings and some deeper QAOA cases.

### Backend-focused benchmark campaign

The backend-focused campaign executed `16` runs across `2` problem cases and `8` solver cases. On this small backend benchmark slice, the decoded optimality ratio remained `1.0` across all backend groups. The backend notes mainly reinforce two conclusions:

- QAOA remained stable across `statevector`, `shot_based`, and `noisy` on these tiny instances, with optimizer success rate `1.0`.
- VQE again showed optimizer-status inconsistencies. The campaign notes report optimizer success rates of `0.0` for statevector VQE and `0.5` for shot-based and noisy VQE, even though the decoded solution quality remained perfect on the same slice. Need to investigate and/or fix this behaviour/problem.

## Discussion

The core software boundary is coherent, the CLI workflows are functional, the tests pass, and the experiment system reliably produces structured outputs and plots.

From a problem-modeling perspective, the repository demonstrates that a single QUBO-centered workflow can support both a direct benchmark like MaxCut and a penalty-based constrained benchmark like Minimum Vertex Cover. This is an important software result because the same experiment interfaces were used across classical and quantum methods.

On the smallest preserved instances, QAOA, VQE, brute force, and OpenJij all reached the same optimal decoded solutions. That is useful as validation. The more informative observations appear in the analysis workflows and the moderate campaign: backend noise degrades QAOA expectation values, warm-start initialization improves depth-2 QAOA expectation quality, and the broader statevector campaign shows that some VQE settings and some QAOA configurations degrade on less trivial six-variable cases.

## Limitations

Several limitations are important for interpreting the study honestly.

First, the benchmark scale is small. The core preserved runs use 4-node examples, and the broader executed campaign reaches only moderate 6-variable cases.

Second, constrained problems require careful metric interpretation. In the moderate campaign, one Minimum Vertex Cover Erdős-Rényi case produced an `optimality_ratio` above `1.0` for an infeasible QAOA run because the aggregate ratio was derived from the decoded objective size while penalty and feasibility were recorded separately. This does not invalidate the run logs, but it means constrained-case summaries must be read together with feasibility and penalty information rather than as standalone evidence.

## Conclusion

The completed repository delivers a coherent and reproducible QUBO/VQA research workflow for small MaxCut and Minimum Vertex Cover benchmarks. It implements transparent QUBO modeling, exact classical references, OpenJij sampling, QAOA, VQE, backend comparisons, initialization studies, landscape analysis, and benchmark campaigns under a shared CLI/config interface.

The executed results confirm that the implementation is operational. The strongest validated outcomes are: the clean end-to-end architecture, the consistency of single-run and aggregate artifact generation, the stability of tiny benchmark solutions across solver families, the meaningful backend and initialization analyses, and the broader moderate campaign that begins to reveal nontrivial performance differences.

## Appendix A: Executed Commands

The report is based on the following executed command set:

```text
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

## Appendix B: Output Location

All result folders used for this report are stored under:

```text
data/results/session-20260415/
```
