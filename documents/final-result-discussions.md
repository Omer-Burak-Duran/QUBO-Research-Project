# Final Result Discussions

This document discusses the final benchmark outputs generated under
`data/results/session-20260506/`. It uses the four completed final-report
folders:

- `final-report-benchmark-campaign-20260506-104854`
- `final-report-backend-campaign-20260506-105015`
- `final-report-qaoa-init-compare-20260506-105117`
- `final-report-landscape-analysis-20260506-105143`

The main conclusion is that the project now has a complete, reproducible QUBO
benchmark pipeline for MaxCut and Minimum Vertex Cover (MVC). The results are
useful for a course-scale research report, but they should not be presented as
evidence of quantum advantage. Every selected instance is still small enough for
an exact brute-force reference.

## Result Sources

| Study | Runs or samples | Most useful artifacts |
| --- | ---: | --- |
| Main solver campaign | `152` runs | `tables/run_metrics.csv`, `tables/solver_family_aggregates.csv`, `tables/case_aggregates.csv`, `notes.md` |
| Backend campaign | `39` runs | `tables/backend_aggregates.csv`, `tables/run_metrics.csv`, backend plots |
| QAOA initialization | `18` QAOA runs | `tables/aggregate_metrics.csv`, `tables/run_metrics.csv`, traces |
| Landscape and gradients | `961` grid points, `6` multi-start runs, `24` gradient samples | landscape CSV, gradient CSVs, heatmaps |

Useful report figures:

- `../data/results/session-20260506/final-report-benchmark-campaign-20260506-104854/plots/optimality_ratio_by_case.png`
- `../data/results/session-20260506/final-report-benchmark-campaign-20260506-104854/plots/runtime_by_case.png`
- `../data/results/session-20260506/final-report-benchmark-campaign-20260506-104854/plots/optimality_ratio_by_solver_family.png`
- `../data/results/session-20260506/final-report-backend-campaign-20260506-105015/plots/optimality_ratio_by_backend.png`
- `../data/results/session-20260506/final-report-qaoa-init-compare-20260506-105117/plots/best_expectation_energy_vs_depth.png`
- `../data/results/session-20260506/final-report-landscape-analysis-20260506-105143/plots/qaoa_p1_landscape_energy.png`
- `../data/results/session-20260506/final-report-landscape-analysis-20260506-105143/plots/qaoa_multistart_convergence.png`
- `../data/results/session-20260506/final-report-landscape-analysis-20260506-105143/plots/qaoa_gradient_norms.png`
- `../data/results/session-20260506/final-report-landscape-analysis-20260506-105143/plots/vqe_gradient_norms.png`

## Main Solver Campaign

The main campaign is the central experimental dataset. It executed `152` runs
across `8` problem cases and `10` solver cases, with exact references available
for every run. It compares brute force, OpenJij, QAOA, and VQE on shared QUBO
encodings.

### Exact Reference Values

| Problem case | Variables | Exact objective | Exact QUBO energy |
| --- | ---: | ---: | ---: |
| `maxcut-cycle-4` | 4 | `4.0` | `-4.0` |
| `maxcut-cycle-6` | 6 | `6.0` | `-6.0` |
| `maxcut-er-6-seed11` | 6 | `6.0` | `-6.0` |
| `maxcut-weighted-er-8-seed17` | 8 | `23.0` | `-23.0` |
| `mvc-path-4` | 4 | `2.0` | `2.0` |
| `mvc-cycle-6` | 6 | `3.0` | `3.0` |
| `mvc-er-6-seed11` | 6 | `3.0` | `3.0` |
| `mvc-er-8-seed17` | 8 | `4.0` | `4.0` |

The sign difference is expected: MaxCut is represented so better cuts map to
lower QUBO energies, while feasible MVC optima have energy equal to cover size
because the penalty term is zero.

### Solver-Family Behavior

| Solver | Runs | Mean optimality | Solution quality | Feasibility | Success flag | Mean runtime (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Brute force | 8 | `1.0000` | `1.0000` | `1.0000` | `1.0000` | `0.0029` |
| OpenJij | 16 | `0.9583` | `0.8750` | `1.0000` | `1.0000` | `0.0524` |
| QAOA | 64 | `0.8275` | `0.7031` | `0.8750` | `0.7031` | `0.0761` |
| VQE | 64 | `0.9553` | `0.8281` | `0.9844` | `0.1250` | `0.1306` |

Brute force behaved exactly as expected and should be treated as the reference,
not as a scalable method. OpenJij was also strong overall, though the two-trial
`maxcut-cycle-6` result had mean optimality `0.6667`; that should be described
as sampling variance rather than a firm conclusion.

QAOA was the most mixed solver family. It did well on several MaxCut cases but
struggled on shallow MVC penalty cases, where infeasible dominant bitstrings
cause feasibility-adjusted optimality to become `0.0`. VQE had high decoded
quality but low optimizer success, especially at depth 2. This is one of the
most important interpretation points: optimizer termination and decoded
solution quality are related but not identical.

### Problem Size and Difficulty

| Slice | Runs | Mean optimality | Solution quality | Feasibility | Mean runtime (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| MaxCut, 4 variables | 19 | `1.0000` | `1.0000` | `1.0000` | `0.0823` |
| MaxCut, 6 variables | 38 | `0.9605` | `0.8421` | `1.0000` | `0.0810` |
| MaxCut, 8 variables | 19 | `0.8650` | `0.4211` | `1.0000` | `0.1089` |
| MVC, 4 variables | 19 | `0.8421` | `0.8421` | `0.8421` | `0.0650` |
| MVC, 6 variables | 38 | `0.9237` | `0.8684` | `0.9474` | `0.0952` |
| MVC, 8 variables | 19 | `0.7579` | `0.6316` | `0.7895` | `0.1331` |

The expected size trend appears clearly. The 4-variable MaxCut cycle is a
validation case, while the 8-variable weighted MaxCut and 8-variable MVC
Erdos-Renyi cases are much more informative. The weighted MaxCut aggregate
reached mean optimality `0.8650`; the 8-variable MVC aggregate reached `0.7579`
and only `0.7895` feasibility.

MVC is not automatically easier just because it has small graphs. The
penalty-based formulation makes feasibility central. For example, shallow QAOA
on some MVC cases produced infeasible dominant bitstrings even when the
optimizer reported success.

### QAOA Depth and Initialization

| QAOA slice | Runs | Mean optimality | Solution quality | Feasibility | Optimizer success |
| --- | ---: | ---: | ---: | ---: | ---: |
| MaxCut `p=1` | 16 | `0.8976` | `0.6250` | `1.0000` | `1.0000` |
| MaxCut `p=2` | 16 | `0.9375` | `0.7500` | `1.0000` | `0.5625` |
| MVC `p=1` | 16 | `0.5000` | `0.5000` | `0.5000` | `0.9375` |
| MVC `p=2` | 16 | `0.9750` | `0.9375` | `1.0000` | `0.3125` |

Depth helped. On MaxCut, `p=2` improved mean optimality from `0.8976` to
`0.9375`. On MVC, the improvement was stronger: feasibility rose from `0.5000`
to `1.0000`, and mean optimality rose from `0.5000` to `0.9750`.

The main campaign also shows that interpolation is not universally safe. On
`mvc-er-6-seed11`, interpolation averaged `0.3000` while random starts averaged
`0.8333`. On `mvc-er-8-seed17`, interpolation averaged `0.5000` while random
starts averaged `0.6667`. This suggests that initialization strategies tuned
for MaxCut may not transfer cleanly to penalty-constrained QUBOs.

### VQE Ansatz and Depth

Problem-aware VQE was generally stronger than hardware-efficient VQE on MVC.
The clearest case was `mvc-er-8-seed17`, where problem-aware VQE had mean
optimality `0.9500` and hardware-efficient VQE had `0.6500`. On MaxCut the
difference was smaller; for the weighted 8-variable case both ansatz families
were reported at `0.9674`.

Depth did not give a clean monotonic story. Depth-2 VQE is more expressive, but
it often hit the `140`-evaluation limit and reported optimizer failure. Some of
those same runs still decoded optimal solutions. For example, problem-aware VQE
depth 2 on MVC had mean optimality `1.0000` with optimizer success `0.0000`.

### Main Bottlenecks

| Case | Solver | Mean optimality | Feasibility | Optimizer success | Interpretation |
| --- | --- | ---: | ---: | ---: | --- |
| `mvc-er-6-seed11` | `qaoa_interpolation_p1` | `0.0000` | `0.0000` | `1.0000` | Optimizer success did not imply feasible decoded solutions. |
| `mvc-er-8-seed17` | `qaoa_interpolation_p1` | `0.0000` | `0.0000` | `1.0000` | Shallow interpolation failed on constrained MVC. |
| `mvc-path-4` | `qaoa_interpolation_p1` | `0.0000` | `0.0000` | `0.0000` | Small constrained cases can still decode infeasibly. |
| `maxcut-weighted-er-8-seed17` | `qaoa_interpolation_p1` | `0.6087` | `1.0000` | `1.0000` | Feasible but low-quality weighted MaxCut result. |

These are the best cases to use when explaining limitations and future work.

## Backend Campaign

The backend campaign used `3` small problem cases and `39` total runs. Decoded
objective quality stayed perfect across statevector, shot-based, and noisy
backends, so the backend discussion should focus on runtime, expectation
energy, and optimizer status rather than decoded optimality.

| Solver | Backend | Runs | Mean optimality | Optimizer success | Mean expectation | Mean runtime (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| QAOA | statevector | 6 | `1.0000` | `1.0000` | `-1.2111` | `0.0818` |
| QAOA | shot_based | 6 | `1.0000` | `1.0000` | `-1.2261` | `0.0180` |
| QAOA | noisy | 6 | `1.0000` | `1.0000` | `-1.0944` | `1.3253` |
| VQE | statevector | 6 | `1.0000` | `0.1667` | `-1.6917` | `0.0437` |
| VQE | shot_based | 6 | `1.0000` | `1.0000` | `-1.5210` | `0.0408` |
| VQE | noisy | 6 | `1.0000` | `0.5000` | `-1.6278` | `3.1589` |

The expected runtime effect is strong: noisy QAOA averaged `1.3253 s`, and
noisy VQE averaged `3.1589 s`. The QAOA expectation-energy aggregate also shows
the expected degradation under noise: noisy QAOA averaged `-1.0944`, compared
with about `-1.21` to `-1.23` for statevector and shot-based runs.

The lack of decoded-quality degradation is not evidence that noise is harmless.
These instances are very small. The better phrasing is that the selected small
backend slice was robust enough that dominant decoded bitstrings remained
optimal, while expectation and runtime still changed.

## QAOA Initialization Study

The initialization study used the 6-variable Erdos-Renyi MaxCut instance with
exact objective `6.0` and exact energy `-6.0`.

| Strategy | Depth | Runs | Mean approximation | Mean expectation | Success rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| interpolation | 1 | 1 | `1.0000` | `-4.4426` | `1.0000` |
| interpolation | 2 | 1 | `1.0000` | `-5.2125` | `1.0000` |
| interpolation | 3 | 1 | `1.0000` | `-4.5576` | `0.0000` |
| warm_start | 1 | 1 | `1.0000` | `-4.4426` | `1.0000` |
| warm_start | 2 | 1 | `1.0000` | `-5.2125` | `1.0000` |
| warm_start | 3 | 1 | `1.0000` | `-5.5875` | `0.0000` |
| random | 1 | 4 | `0.9167` | `-4.0011` | `1.0000` |
| random | 2 | 4 | `1.0000` | `-5.1067` | `0.7500` |
| random | 3 | 4 | `1.0000` | `-5.0549` | `0.0000` |

The expected result is that depth improves the variational objective. The
strongest expectation energy was warm-start `p=3` at `-5.5875`, supporting the
idea that reusing lower-depth optimized parameters can help higher-depth QAOA.

The caution is that all `p=3` groups reported optimizer success `0.0000`, even
though they decoded optimal objective values. Random `p=1` also exposed
initialization sensitivity: two random trials decoded objective `5.0`
(`0.8333` approximation), while interpolation and warm-start decoded `6.0`.

## Landscape and Gradient Study

The landscape study used the same 6-variable Erdos-Renyi MaxCut instance. The
QAOA `p=1` grid scanned `961` parameter points. The best grid point was:

- `gamma = 0.7330382858376183`
- `beta = 1.1519173063162573`
- expectation energy `-4.4310744638723545`
- dominant bitstring `[1, 0, 1, 1, 0, 0]`
- decoded objective `6.0`
- approximation ratio `1.0000`
- dominant probability `0.12587098530090898`

This is close to the optimized `p=1` expectation from the initialization study
(`-4.4426`), which validates that the optimizer is finding a region visible in
the explicit grid scan.

| Decoded objective | Grid points | Approximation ratio |
| ---: | ---: | ---: |
| `0.0` | 256 | `0.0000` |
| `1.0` | 112 | `0.1667` |
| `2.0` | 147 | `0.3333` |
| `3.0` | 10 | `0.5000` |
| `4.0` | 127 | `0.6667` |
| `5.0` | 118 | `0.8333` |
| `6.0` | 191 | `1.0000` |

The distribution shows why expectation energy and decoded objective quality
must both be reported. Expectation energy changes smoothly, while the dominant
decoded objective changes in plateaus and jumps.

The QAOA multi-start study ran `6` random starts at `p=1`. All optimizer runs
reported success, but only `2` of `6` decoded the exact objective `6.0`; the
other `4` decoded objective `5.0`. The mean best expectation energy was
`-3.8539`. This reinforces the initialization sensitivity seen elsewhere.

| Model | Samples | Mean gradient norm | Min | Max | Variance |
| --- | ---: | ---: | ---: | ---: | ---: |
| QAOA `p=1` | 12 | `2.1902` | `0.8645` | `5.3132` | `1.5523` |
| VQE hardware-efficient depth 1 | 12 | `0.8060` | `0.4079` | `1.0405` | `0.0258` |

These gradient statistics do not demonstrate a barren plateau. The instances
are too small and the sample count is limited. What they do show is that QAOA
had larger and more variable sampled gradients than the selected VQE ansatz on
this instance.

## Expected Results

Brute force found every exact optimum, which validates the references and makes
the aggregate optimality ratios meaningful.

Increasing QAOA depth often improved expectation energy or decoded quality. The
main campaign showed MaxCut mean optimality increasing from `0.8976` at `p=1`
to `0.9375` at `p=2`, and the initialization study showed interpolation energy
improving from `-4.4426` to `-5.2125`.

Noisy simulation increased runtime substantially, as expected. Weighted and
random graph cases were harder than simple cycle cases, also as expected.

## Unexpected or Cautionary Results

The biggest caution is the gap between optimizer success and decoded solution
quality. VQE had strong decoded quality but low optimizer success in the main
campaign. QAOA `p=3` decoded optimal bitstrings despite optimizer failure.

QAOA interpolation was weak on several constrained MVC cases. This suggests
that a good initialization strategy for MaxCut is not automatically a good
strategy for penalty-constrained QUBOs.

The backend campaign did not show decoded-quality degradation under noise. This
is not a contradiction of noise sensitivity theory; the backend cases are small
enough that dominant decoded bitstrings remained optimal.

## What Is and Is Not Conclusive

It is conclusive that the repository can produce reproducible, report-ready
QUBO benchmark artifacts across classical baselines, QAOA, VQE, backend modes,
initialization strategies, and landscape analysis.

It is conclusive that harder random, weighted, and constrained cases expose
performance differences that are hidden on the smallest cycle instances.

It is not conclusive that QAOA is generally better than VQE, or vice versa. The
answer depends on problem family, initialization, ansatz, depth, backend, and
whether the metric is expectation energy or decoded objective quality.

It is not conclusive that these experiments show barren plateaus or hardware
noise behavior. The gradient study is exploratory, and the backend study uses
simulated shot-based and noisy paths rather than physical hardware.

## Recommended Report Usage

Use the main campaign as the central results section. Use the backend campaign
as a focused backend-behavior subsection. Use the initialization study to
explain optimizer-start sensitivity, especially the strong warm-start `p=3`
expectation result. Use the landscape study to explain why smooth expectation
energy and discrete decoded objective quality are related but distinct.

The final report should frame the project as a successful small-scale research
workflow, not as a speedup claim.
