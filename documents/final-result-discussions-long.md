# Final Result Discussions

This document discusses the final benchmark outputs generated under
`data/results/session-20260506/`. The discussion is based on the four final
experiment folders:

- `final-report-benchmark-campaign-20260506-104854`
- `final-report-backend-campaign-20260506-105015`
- `final-report-qaoa-init-compare-20260506-105117`
- `final-report-landscape-analysis-20260506-105143`

The benchmark suite is intentionally small and exact-reference driven. Its main
purpose is not to claim quantum speedup. Its purpose is to demonstrate a
complete, reproducible QUBO research pipeline: encode MaxCut and Minimum Vertex
Cover, convert QUBO to Ising for variational solvers, run classical and quantum
methods on shared instances, save raw artifacts, and interpret solver behavior
through aggregate tables, plots, initialization studies, and landscape analysis.

## Executive Interpretation

The final experiments support four main conclusions.

First, the QUBO-centered modeling pipeline is working. Every final benchmark run
had an exact reference, and the output folders contain the expected structured
artifacts: `summary.json`, aggregate CSV tables, per-run result files, QUBO and
Ising artifacts, traces, notes, and plots.

Second, the easiest structured instances are solved by almost every method, so
they are best interpreted as validation cases. For example, all solver groups
achieved mean optimality ratio `1.0000` on `maxcut-cycle-4`, and the
`mvc-cycle-6` aggregate also reached mean optimality ratio `1.0000`.

Third, the harder cases reveal useful differences. The weighted 8-variable
MaxCut instance and the 8-variable Minimum Vertex Cover Erdos-Renyi instance
are the clearest stress tests. The weighted MaxCut aggregate had mean
optimality ratio `0.8650`, and the 8-variable MVC aggregate had mean optimality
ratio `0.7579`. These are the most important cases for showing that the final
dataset is not only a collection of trivial successes.

Fourth, optimizer status and decoded solution quality should be discussed
separately. Several QAOA and VQE runs found optimal decoded bitstrings even
when COBYLA reported failure or hit the iteration cap. This is not a bug in the
artifact structure; it is a meaningful variational-optimization caveat.

## Output Map

| Study | Folder | Primary evidence |
| --- | --- | --- |
| Main solver campaign | `data/results/session-20260506/final-report-benchmark-campaign-20260506-104854` | `tables/run_metrics.csv`, `tables/solver_family_aggregates.csv`, `tables/case_aggregates.csv`, `notes.md` |
| Backend campaign | `data/results/session-20260506/final-report-backend-campaign-20260506-105015` | `tables/backend_aggregates.csv`, `tables/run_metrics.csv`, backend plots |
| QAOA initialization | `data/results/session-20260506/final-report-qaoa-init-compare-20260506-105117` | `tables/aggregate_metrics.csv`, `tables/run_metrics.csv`, traces |
| Landscape and gradients | `data/results/session-20260506/final-report-landscape-analysis-20260506-105143` | `tables/qaoa_p1_landscape.csv`, gradient CSVs, heatmaps |

The most useful saved figures for the final report are:

- `../data/results/session-20260506/final-report-benchmark-campaign-20260506-104854/plots/optimality_ratio_by_case.png`
- `../data/results/session-20260506/final-report-benchmark-campaign-20260506-104854/plots/runtime_by_case.png`
- `../data/results/session-20260506/final-report-benchmark-campaign-20260506-104854/plots/optimality_ratio_by_solver_family.png`
- `../data/results/session-20260506/final-report-backend-campaign-20260506-105015/plots/optimality_ratio_by_backend.png`
- `../data/results/session-20260506/final-report-qaoa-init-compare-20260506-105117/plots/best_expectation_energy_vs_depth.png`
- `../data/results/session-20260506/final-report-landscape-analysis-20260506-105143/plots/qaoa_p1_landscape_energy.png`
- `../data/results/session-20260506/final-report-landscape-analysis-20260506-105143/plots/qaoa_multistart_convergence.png`
- `../data/results/session-20260506/final-report-landscape-analysis-20260506-105143/plots/qaoa_gradient_norms.png`
- `../data/results/session-20260506/final-report-landscape-analysis-20260506-105143/plots/vqe_gradient_norms.png`

## Main Statevector Benchmark Campaign

The main campaign executed `152` total runs across `8` problem cases and `10`
solver cases. Every run had an exact brute-force reference. This makes the
campaign the strongest evidence source for solver-family comparisons, problem
family behavior, size effects, QAOA depth effects, and VQE ansatz/depth effects.

### Exact References

| Problem case | Family | Variables | Exact objective | Exact QUBO energy |
| --- | --- | ---: | ---: | ---: |
| `maxcut-cycle-4` | MaxCut cycle | 4 | `4.0` | `-4.0` |
| `maxcut-cycle-6` | MaxCut cycle | 6 | `6.0` | `-6.0` |
| `maxcut-er-6-seed11` | MaxCut Erdos-Renyi | 6 | `6.0` | `-6.0` |
| `maxcut-weighted-er-8-seed17` | Weighted MaxCut Erdos-Renyi | 8 | `23.0` | `-23.0` |
| `mvc-path-4` | MVC path | 4 | `2.0` | `2.0` |
| `mvc-cycle-6` | MVC cycle | 6 | `3.0` | `3.0` |
| `mvc-er-6-seed11` | MVC Erdos-Renyi | 6 | `3.0` | `3.0` |
| `mvc-er-8-seed17` | MVC Erdos-Renyi | 8 | `4.0` | `4.0` |

The sign difference between MaxCut and MVC energies is expected. MaxCut is
represented so better cuts correspond to lower QUBO energies after conversion,
while MVC is a minimization problem with penalty terms, so the optimum energy is
the cover size when all constraints are satisfied.

### Solver-Family Summary

| Solver family | Runs | Mean optimality ratio | Solution quality rate | Feasibility rate | Optimizer/sampler success | Mean runtime (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Brute force | 8 | `1.0000` | `1.0000` | `1.0000` | `1.0000` | `0.0029` |
| OpenJij | 16 | `0.9583` | `0.8750` | `1.0000` | `1.0000` | `0.0524` |
| QAOA | 64 | `0.8275` | `0.7031` | `0.8750` | `0.7031` | `0.0761` |
| VQE | 64 | `0.9553` | `0.8281` | `0.9844` | `0.1250` | `0.1306` |

The brute-force results behave exactly as expected: perfect quality, perfect
feasibility, and the fastest runtime at this small scale. Brute force is the
reference, not a scalable benchmark method.

OpenJij is also mostly consistent with expectation. It remains feasible on all
decoded cases and reaches near-optimal quality overall. Its weakest aggregate
case was `maxcut-cycle-6`, where `openjij_sa` reached mean optimality ratio
`0.6667` in the two trials. That is somewhat surprising because cycles are
usually easy, but with only two trials this is better treated as sampler
variance than a strong conclusion about OpenJij.

QAOA is more mixed. It performs well on several MaxCut cases but struggles on
some MVC penalty cases, especially at `p=1`. Its mean optimality ratio is lower
than VQE in the full statevector campaign, mainly because infeasible MVC
solutions are assigned feasibility-adjusted optimality ratio `0.0`.

VQE has the most important status-quality gap. Its decoded solution quality is
high, with mean optimality ratio `0.9553`, but optimizer success is only
`0.1250`. Many VQE depth-2 runs hit the configured iteration cap while still
returning good dominant bitstrings. The report should therefore avoid equating
COBYLA success with solution quality.

### Problem and Size Effects

| Problem slice | Runs | Mean optimality ratio | Solution quality rate | Feasibility rate | Mean runtime (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| MaxCut, 4 variables | 19 | `1.0000` | `1.0000` | `1.0000` | `0.0823` |
| MaxCut, 6 variables | 38 | `0.9605` | `0.8421` | `1.0000` | `0.0810` |
| MaxCut, 8 variables | 19 | `0.8650` | `0.4211` | `1.0000` | `0.1089` |
| MVC, 4 variables | 19 | `0.8421` | `0.8421` | `0.8421` | `0.0650` |
| MVC, 6 variables | 38 | `0.9237` | `0.8684` | `0.9474` | `0.0952` |
| MVC, 8 variables | 19 | `0.7579` | `0.6316` | `0.7895` | `0.1331` |

The size trend is directionally expected: the 8-variable cases are harder than
the 4-variable cases. For MaxCut, the weighted 8-variable Erdos-Renyi instance
is clearly the hardest case. For MVC, the 8-variable Erdos-Renyi graph is also
the hardest aggregate slice, with both lower feasibility and lower optimality.

The MVC path-4 result is a useful caution. Although it is small, QAOA `p=1`
produced infeasible dominant bitstrings for some runs. This shows that
constraint penalties can make a small constrained problem harder to decode
correctly than an unconstrained MaxCut problem of similar size.

### QAOA Depth and Initialization Signals

In the main campaign, QAOA depth had different effects for MaxCut and MVC.

| QAOA slice | Runs | Mean optimality ratio | Solution quality rate | Feasibility rate | Optimizer success |
| --- | ---: | ---: | ---: | ---: | ---: |
| MaxCut `p=1` | 16 | `0.8976` | `0.6250` | `1.0000` | `1.0000` |
| MaxCut `p=2` | 16 | `0.9375` | `0.7500` | `1.0000` | `0.5625` |
| MVC `p=1` | 16 | `0.5000` | `0.5000` | `0.5000` | `0.9375` |
| MVC `p=2` | 16 | `0.9750` | `0.9375` | `1.0000` | `0.3125` |

The MaxCut result is theoretically reasonable: increasing depth from `p=1` to
`p=2` improves mean optimality from `0.8976` to `0.9375`, though optimizer
success decreases. The MVC result is more striking. Increasing from `p=1` to
`p=2` changes feasibility from `0.5000` to `1.0000` and mean optimality from
`0.5000` to `0.9750`. This suggests that the additional QAOA layer helps move
probability mass toward feasible cover states, even if the optimizer reports
success less often.

The main campaign also suggests that random QAOA starts can outperform
interpolation on constrained MVC cases. For `mvc-er-6-seed11`, interpolation
averaged `0.3000` while random starts averaged `0.8333`. For `mvc-er-8-seed17`,
interpolation averaged `0.5000` while random starts averaged `0.6667`. This is
not enough to prove random initialization is better generally, but it does show
that interpolation is not universally safe when penalty constraints dominate
the energy landscape.

### VQE Ansatz and Depth Signals

Problem-aware VQE is generally stronger than hardware-efficient VQE on the MVC
cases in this run. The clearest example is `mvc-er-8-seed17`, where the notes
report problem-aware mean optimality `0.9500` and hardware-efficient mean
optimality `0.6500`. On MaxCut, the difference is smaller. For the weighted
8-variable MaxCut case, both ansatz families reached `0.9674` in the structured
comparison notes.

Depth does not provide a simple monotonic improvement for VQE. Depth-2 runs
have more expressive circuits, but they also always used the configured maximum
of `140` evaluations in the aggregate slices and often reported optimizer
failure. For example, problem-aware VQE depth 2 on MVC reached mean optimality
`1.0000` with optimizer success `0.0000`. This is a useful result: decoded
quality can be strong even when the optimizer termination criterion says the
optimization did not converge.

### Main Campaign Bottlenecks

The most important weak cases were:

| Case | Solver | Mean optimality | Feasibility | Optimizer success | Interpretation |
| --- | --- | ---: | ---: | ---: | --- |
| `mvc-er-6-seed11` | `qaoa_interpolation_p1` | `0.0000` | `0.0000` | `1.0000` | Optimizer success did not imply feasible decoded solutions. |
| `mvc-er-8-seed17` | `qaoa_interpolation_p1` | `0.0000` | `0.0000` | `1.0000` | Shallow interpolation failed on constrained MVC. |
| `mvc-path-4` | `qaoa_interpolation_p1` | `0.0000` | `0.0000` | `0.0000` | Small size did not prevent infeasible dominant output. |
| `maxcut-weighted-er-8-seed17` | `qaoa_interpolation_p1` | `0.6087` | `1.0000` | `1.0000` | Feasible but low-quality weighted MaxCut solution. |
| `maxcut-weighted-er-8-seed17` | `qaoa_random_p2` | `0.7246` | `1.0000` | `0.3333` | Depth helped somewhat but did not reliably reach optimum. |

These are the best cases to discuss when explaining limitations and future work.

## Backend Campaign

The backend campaign executed `39` total runs across `3` small problem cases and
`7` solver cases. It compared statevector, shot-based, and noisy execution for
QAOA and VQE on small MaxCut and MVC instances.

The most important result is that decoded objective quality stayed perfect
across all backend groups. Every QAOA and VQE backend group had mean optimality
ratio `1.0000` and solution quality rate `1.0000`. Therefore, this campaign
does not provide evidence that backend noise degraded decoded objective quality
on these small instances. Instead, its useful signal is in expectation energy,
runtime, and optimizer status.

| Solver | Backend | Runs | Mean optimality | Optimizer success | Mean expectation energy | Mean runtime (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| QAOA | statevector | 6 | `1.0000` | `1.0000` | `-1.2111` | `0.0818` |
| QAOA | shot_based | 6 | `1.0000` | `1.0000` | `-1.2261` | `0.0180` |
| QAOA | noisy | 6 | `1.0000` | `1.0000` | `-1.0944` | `1.3253` |
| VQE | statevector | 6 | `1.0000` | `0.1667` | `-1.6917` | `0.0437` |
| VQE | shot_based | 6 | `1.0000` | `1.0000` | `-1.5210` | `0.0408` |
| VQE | noisy | 6 | `1.0000` | `0.5000` | `-1.6278` | `3.1589` |

The expected result is that noisy simulation is slower. This appears strongly:
QAOA noisy mean runtime was `1.3253 s`, compared with `0.0818 s` statevector
and `0.0180 s` shot-based. VQE noisy mean runtime was `3.1589 s`, much larger
than either statevector or shot-based VQE.

The expectation-energy results are more nuanced. QAOA noisy had a worse mean
expectation energy than statevector and shot-based (`-1.0944` versus around
`-1.21` to `-1.23`), consistent with simulated noise degrading the variational
objective. VQE does not show the same simple ordering in the aggregate mean
because the small problem set mixes MaxCut and MVC energy scales and because
optimization paths differ across stochastic backends.

The shot-based backend should be described carefully. In this codebase it is
finite-shot sampling from ideal probabilities, not hardware noise. Its strong
performance here means that `1024` shots were enough for these small cases; it
does not mean shot noise is irrelevant at larger scales.

## QAOA Initialization Study

The initialization study used the 6-variable Erdos-Renyi MaxCut instance with
exact optimum objective `6.0` and exact QUBO energy `-6.0`. It ran `18` QAOA
experiments across interpolation, warm-start, and random initialization for
depths `p=1`, `p=2`, and `p=3`.

| Strategy | Depth | Runs | Mean objective | Mean approximation | Mean expectation energy | Success rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| interpolation | 1 | 1 | `6.0` | `1.0000` | `-4.4426` | `1.0000` |
| interpolation | 2 | 1 | `6.0` | `1.0000` | `-5.2125` | `1.0000` |
| interpolation | 3 | 1 | `6.0` | `1.0000` | `-4.5576` | `0.0000` |
| warm_start | 1 | 1 | `6.0` | `1.0000` | `-4.4426` | `1.0000` |
| warm_start | 2 | 1 | `6.0` | `1.0000` | `-5.2125` | `1.0000` |
| warm_start | 3 | 1 | `6.0` | `1.0000` | `-5.5875` | `0.0000` |
| random | 1 | 4 | `5.5` | `0.9167` | `-4.0011` | `1.0000` |
| random | 2 | 4 | `6.0` | `1.0000` | `-5.1067` | `0.7500` |
| random | 3 | 4 | `6.0` | `1.0000` | `-5.0549` | `0.0000` |

The main expected result is visible: depth `p=2` improves expectation energy
relative to `p=1` for interpolation, warm-start, and random starts. The
best depth-2 expectation values cluster around `-5.21`, while the common `p=1`
optimum is around `-4.44`.

The most interesting result is warm-start at `p=3`. It achieved the strongest
best expectation energy in the study, `-5.5875`, while still decoding to the
optimal objective `6.0`. This supports the theoretical idea that reusing
lower-depth optimized parameters can help higher-depth QAOA optimization.

The unexpected or at least non-conclusive part is the optimizer success rate at
`p=3`. All `p=3` groups reported success rate `0.0000`, but most still decoded
to the optimal objective. This means the configured COBYLA iteration cap is too
tight to treat the success flag as the main quality metric. For the report,
describe this as optimizer-status limitation rather than algorithmic failure.

Random `p=1` exposed initialization sensitivity. Two random `p=1` trials
decoded objective `5.0`, giving approximation ratio `0.8333`, while the
interpolation and warm-start `p=1` runs decoded objective `6.0`. At higher
depth, random starts recovered the exact decoded optimum in all trials, though
expectation energy varied.


## Landscape and Gradient Study

The landscape study used the same 6-variable Erdos-Renyi MaxCut instance as the
initialization study. The exact reference was objective `6.0` and QUBO energy
`-6.0`.

The QAOA `p=1` grid scanned `961` points over `gamma` and `beta`. The best grid
point was:

- `gamma = 0.7330382858376183`
- `beta = 1.1519173063162573`
- expectation energy `-4.4310744638723545`
- dominant bitstring `[1, 0, 1, 1, 0, 0]`
- decoded objective `6.0`
- approximation ratio `1.0000`
- dominant probability `0.12587098530090898`

The best grid expectation is close to the optimized `p=1` expectation from the
initialization study, which was about `-4.4426`. That agreement is useful
validation: the optimizer is finding a region that also appears in the explicit
landscape scan.

The objective landscape is highly piecewise. Out of `961` grid points, the
dominant decoded objective distribution was:

| Decoded objective | Grid points | Approximation ratio |
| ---: | ---: | ---: |
| `0.0` | 256 | `0.0000` |
| `1.0` | 112 | `0.1667` |
| `2.0` | 147 | `0.3333` |
| `3.0` | 10 | `0.5000` |
| `4.0` | 127 | `0.6667` |
| `5.0` | 118 | `0.8333` |
| `6.0` | 191 | `1.0000` |

This explains why expectation energy and decoded quality should both be
reported. The expectation landscape changes smoothly with parameters, but the
dominant bitstring can remain constant over regions and jump abruptly between
objective values.

The multi-start experiment ran `6` random-start QAOA optimizations at `p=1`.
All optimizer runs reported success, but only `2` of `6` decoded the exact
objective `6.0`; the other `4` decoded objective `5.0`. The mean best
expectation energy was `-3.8539`. This is an important contrast with the
initialization study: shallow random QAOA can converge successfully while still
settling into a suboptimal decoded solution.

The finite-difference gradient statistics were:

| Model | Samples | Mean gradient norm | Min gradient norm | Max gradient norm | Variance |
| --- | ---: | ---: | ---: | ---: | ---: |
| QAOA `p=1` | 12 | `2.1902` | `0.8645` | `5.3132` | `1.5523` |
| VQE hardware-efficient depth 1 | 12 | `0.8060` | `0.4079` | `1.0405` | `0.0258` |

These results do not demonstrate a barren plateau. The instances are too small
and the sample count is too limited for that claim. What they do show is that
the QAOA objective has larger and more variable sampled gradients than the
chosen VQE hardware-efficient ansatz on this instance. That is useful as a
first-pass trainability comparison, but it should be framed as exploratory.

## Expected Results

Several outcomes match theoretical expectations.

Brute force found every exact optimum and is the correct reference for this
small-scale study. This confirms that the exact-reference path is working and
that all aggregate optimality ratios are interpretable.

Increasing QAOA depth often improved expectation energy. This is visible in
both the main campaign and the initialization study. For MaxCut in the main
campaign, mean optimality improved from `0.8976` at `p=1` to `0.9375` at
`p=2`. In the initialization study, interpolation improved from `-4.4426` at
`p=1` to `-5.2125` at `p=2`.

Noisy simulation increased runtime substantially. This is especially clear in
the backend campaign, where noisy QAOA averaged `1.3253 s` and noisy VQE
averaged `3.1589 s`.

The weighted 8-variable MaxCut and 8-variable MVC cases were harder than the
small cycle cases. This is consistent with the expectation that random graph
structure, weights, and constrained penalties create more difficult landscapes
than simple cycles.

## Unexpected or Cautionary Results

The most important unexpected result is that optimizer success and solution
quality often diverged. VQE had high decoded quality but low optimizer success
in the main campaign. QAOA `p=3` initialization runs decoded optimal bitstrings
despite reporting optimizer failure. This means the final report should always
distinguish `optimizer_reported_success`, `solution_quality_success`, and
`optimality_ratio`.

QAOA interpolation was not robust on constrained MVC cases in the main campaign.
For several MVC cases, shallow interpolation produced infeasible dominant
bitstrings even when the optimizer reported success. This shows that
initialization heuristics that behave well for MaxCut do not automatically
transfer to penalty-constrained QUBOs.

The backend campaign did not show decoded-quality degradation under noise. That
is not a contradiction of noise sensitivity theory; the instances are simply
small enough that the dominant decoded bitstring remained optimal. The backend
discussion should focus on expectation energy and runtime rather than claiming
that noise had no effect.

OpenJij underperformed on `maxcut-cycle-6` in this small two-trial campaign.
Because the trial count is low, this should be treated as a stochastic sampling
observation, not as strong evidence that OpenJij is weak on cycles.

## What Is Conclusive

It is reasonable to claim that the project has a working reproducible pipeline
for QUBO modeling, exact references, classical sampling, QAOA, VQE, backend
comparison, initialization analysis, and landscape/gradient analysis.

It is also reasonable to claim that the final benchmark suite reveals meaningful
differences between trivial cycle cases and harder random or weighted cases.
The aggregate metrics show clear degradation on the weighted 8-variable MaxCut
and 8-variable MVC cases.

It is reasonable to claim that QAOA depth, initialization strategy, and VQE
ansatz family matter in practice, even at small scale.

## What Is Not Conclusive

The results do not establish quantum advantage. All benchmark cases are small
enough for exact brute-force references, and brute force remains fastest at this
scale.

The results do not establish that QAOA is better than VQE or vice versa in a
general sense. Their relative performance depends on problem family, depth,
ansatz, initialization, backend, and the distinction between expectation energy
and decoded dominant-bitstring quality.

The gradient study does not establish barren plateaus. It is a small empirical
trainability snapshot with `12` gradient samples for QAOA and `12` for VQE.

The backend study does not establish hardware behavior. Shot-based runs are
finite samples from ideal probabilities, and noisy runs are Aer simulations
with the configured `depolarizing_readout` noise model.

## Recommended Use in the Final Report

Use the main campaign as the central results section. The most useful tables
are `solver_family_aggregates.csv`, `case_aggregates.csv`,
`problem_size_aggregates.csv`, `qaoa_depth_aggregates.csv`, and
`vqe_depth_aggregates.csv`.

Use the backend campaign as a smaller focused subsection. Emphasize that
decoded quality stayed optimal, while runtime and expectation energy changed.
Use the initialization study to explain why optimizer starting points matter.
The strongest concise result is that warm-start `p=3` reached the best
expectation energy, `-5.5875`, while shallow random starts sometimes decoded
only objective `5.0`.

Use the landscape study for visual interpretation. The QAOA heatmap and
multi-start convergence plot are the best figures for explaining why smooth
expectation optimization and discrete decoded objective quality are related but
not identical.

The final report should explicitly state that these are course-scale,
exact-reference benchmarks. Their value is methodological and interpretive:
they demonstrate a complete benchmark pipeline and expose realistic solver
behavior on controlled small instances.
