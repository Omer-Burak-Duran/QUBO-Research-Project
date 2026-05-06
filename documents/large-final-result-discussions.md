# Large Final Result Discussions

This document discusses the large final benchmark outputs generated under
`data/results/session-20260506-large/`.

The discussion is based on these completed experiment folders:

| Study | Folder | Primary evidence |
| --- | --- | --- |
| Smoke validation | `large-final-report-smoke-campaign-20260506-155904` | schema and artifact sanity check |
| Main solver campaign | `large-final-report-benchmark-campaign-20260506-155950` | solver, problem, size, QAOA-depth, and VQE-depth tables |
| Backend campaign | `large-final-report-backend-campaign-20260506-162605` | exact, shot-based, and noisy backend tables |
| QAOA initialization | five `large-final-report-qaoa-init-*` folders | interpolation, warm-start, and random-start tables |
| Landscape and gradients | four `large-final-report-landscape-*` folders | QAOA heatmaps, multi-start traces, gradient statistics |

The large benchmark is still a course-scale exact-reference study. It gives a much stronger empirical
basis than the first final benchmark, but it still should not be interpreted as quantum advantage or as
publication-scale performance evidence.

## Executive Interpretation

The large run supports six main conclusions.

First, the full QUBO-centered pipeline remained stable at the larger local scale. The main campaign
completed `1829` runs across `31` problem cases, and every run had an exact reference. This is important
because all optimality ratios, feasibility rates, and bottleneck discussions are anchored to brute-force
truth values.

Second, the larger dataset is more informative than the first final run. The simple validation cases are
still easy, but the weighted MaxCut and random Minimum Vertex Cover cases expose clear solver differences.
For example, the main campaign mean optimality ratio was `0.9620` for OpenJij, `0.8601` for QAOA, and
`0.9119` for VQE. These averages hide important problem-family effects: QAOA and VQE are strong on
MaxCut but less reliable on constrained MVC cases.

Third, QAOA depth behaved as expected for MaxCut. Mean MaxCut QAOA optimality increased from `0.8542` at
`p = 1` to `0.9638` at `p = 4`. This is the clearest depth-scaling result in the large benchmark.
However, optimizer success decreased at higher depth, so the result should be reported as an
expectation/quality improvement with a growing optimization burden.

Fourth, MVC is the main source of difficulty. Shallow QAOA interpolation often produced infeasible MVC
dominant bitstrings even when the optimizer reported success. Several worst-case rows have
`optimizer_success_rate = 1.0000` and `feasibility_rate = 0.0000`. This is not a logging error; it is a
central constrained-QUBO result.

Fifth, VQE produced good decoded quality despite very low optimizer success. In the main campaign, VQE had
mean optimality ratio `0.9119`, but optimizer success rate only `0.0632`. This confirms that optimizer
termination status and decoded solution quality must be discussed separately.

Sixth, backend effects became visible in the larger backend campaign. Statevector remained the cleanest
reference, shot-based results were close but lower, and noisy simulations were much slower. For VQE,
noisy runs averaged `17.2031 s`, compared with `0.4747 s` for statevector and `0.4493 s` for shot-based
runs.

## Output Map

The most useful artifacts for final-report writing are:

- `data/results/session-20260506-large/large-final-report-benchmark-campaign-20260506-155950/tables/solver_family_aggregates.csv`
- `data/results/session-20260506-large/large-final-report-benchmark-campaign-20260506-155950/tables/problem_size_aggregates.csv`
- `data/results/session-20260506-large/large-final-report-benchmark-campaign-20260506-155950/tables/qaoa_depth_aggregates.csv`
- `data/results/session-20260506-large/large-final-report-benchmark-campaign-20260506-155950/tables/vqe_depth_aggregates.csv`
- `data/results/session-20260506-large/large-final-report-backend-campaign-20260506-162605/tables/backend_aggregates.csv`
- each QAOA initialization folder's `tables/aggregate_metrics.csv`
- each landscape folder's `summary.json` and `tables/qaoa_p1_landscape.csv`

The most useful figures are:

- main campaign `plots/optimality_ratio_by_case.png`
- main campaign `plots/runtime_by_case.png`
- main campaign `plots/optimality_ratio_by_solver_family.png`
- main campaign `plots/optimality_ratio_by_problem_family.png`
- backend campaign `plots/optimality_ratio_by_backend.png`
- initialization-study `plots/best_expectation_energy_vs_depth.png`
- landscape-study `plots/qaoa_p1_landscape_energy.png`
- landscape-study `plots/qaoa_p1_landscape_objective.png`
- landscape-study `plots/qaoa_multistart_convergence.png`
- landscape-study `plots/qaoa_gradient_norms.png` and `plots/vqe_gradient_norms.png`

## Main Statevector Campaign

The main campaign is the central evidence source. It included `17` MaxCut cases and `14` MVC cases, with
sizes up to `n = 12`. For every problem, the exact search space was at most `2^12 = 4096` bitstrings, so
brute force remained practical and exact references were available for all runs.

| Solver family | Runs | Mean optimality | Quality rate | Feasibility | Optimizer success | Mean runtime (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Brute force | `31` | `1.0000` | `1.0000` | `1.0000` | n/a | `0.0606` |
| OpenJij | `310` | `0.9620` | `0.8548` | `1.0000` | n/a | `0.1639` |
| QAOA | `744` | `0.8601` | `0.6317` | `0.9503` | `0.6022` | `0.7857` |
| VQE | `744` | `0.9119` | `0.6169` | `0.9637` | `0.0632` | `0.8505` |

Brute force should be treated as the reference, not as a scalable solver. It was exact, feasible, and
fast because the selected sizes were intentionally small enough for exhaustive search.

OpenJij became much easier to interpret in the large campaign because it had `10` trials per problem
case. Its overall mean optimality was high, and it stayed feasible on all decoded runs. This is expected:
simulated annealing is a strong small-QUBO stochastic baseline. The interesting exception is that OpenJij
was weaker on cycle graphs in the aggregate than on random/path cases. This should be treated as a
configuration-and-sampler observation, not a claim that cycles are intrinsically hard for OpenJij.

QAOA showed the clearest algorithmic trends. On MaxCut, increasing depth improved average quality. On MVC,
depth also helped substantially from `p = 1` to `p = 3`, mostly by improving feasibility, but `p = 4` did
not improve the mean over `p = 3`. This is a useful result: deeper QAOA can help, but finite optimizer
budgets and penalty constraints prevent monotonic decoded-quality guarantees.

VQE was stronger than QAOA in the overall mean, but its optimizer success rate was much lower. This means
VQE's decoded bitstrings often looked good even when COBYLA hit iteration caps or failed its termination
criterion. In the final report, VQE should be discussed with three separate quantities: decoded
optimality, expectation energy, and optimizer success.

## Problem Family And Size Effects

The size aggregates show that the large benchmark added real stress compared with the first final run.

| Problem slice | Runs | Mean optimality | Quality rate | Feasibility | Runtime (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| MaxCut, 4 variables | `59` | `1.0000` | `1.0000` | `1.0000` | `0.1586` |
| MaxCut, 8 variables | `295` | `0.9521` | `0.7695` | `1.0000` | `0.4032` |
| MaxCut, 10 variables | `295` | `0.9404` | `0.5763` | `1.0000` | `0.6132` |
| MaxCut, 12 variables | `295` | `0.9247` | `0.5864` | `1.0000` | `1.2399` |
| MVC, 8 variables | `236` | `0.8794` | `0.7373` | `0.9407` | `0.4494` |
| MVC, 10 variables | `236` | `0.8438` | `0.6314` | `0.9195` | `0.7247` |
| MVC, 12 variables | `236` | `0.7691` | `0.4703` | `0.8856` | `1.1474` |

The MaxCut trend is directionally expected: larger and weighted/random cases reduce mean optimality, but
feasibility is always `1.0000` because MaxCut has no constraint-feasibility layer in the decoder.

The MVC trend is more severe. Mean optimality falls from `0.8794` at 8 variables to `0.7691` at 12
variables, while feasibility also falls. This is the clearest evidence that constrained penalty QUBOs are
harder to decode reliably than unconstrained MaxCut QUBOs at the same variable count.

By problem family, QAOA averaged `0.9193` on MaxCut but `0.7883` on MVC. VQE averaged `0.9678` on MaxCut
but `0.8441` on MVC. This cross-family gap is one of the strongest final-report results.

## QAOA Depth And Initialization

The main campaign QAOA depth aggregates are:

| Problem | QAOA depth | Runs | Mean optimality | Quality rate | Feasibility | Optimizer success |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MaxCut | `1` | `102` | `0.8542` | `0.5000` | `1.0000` | `0.9902` |
| MaxCut | `2` | `102` | `0.9208` | `0.6667` | `1.0000` | `0.7059` |
| MaxCut | `3` | `102` | `0.9383` | `0.6961` | `1.0000` | `0.3824` |
| MaxCut | `4` | `102` | `0.9638` | `0.7647` | `1.0000` | `0.3235` |
| MVC | `1` | `84` | `0.5821` | `0.4405` | `0.6905` | `1.0000` |
| MVC | `2` | `84` | `0.8228` | `0.5595` | `0.9524` | `0.8810` |
| MVC | `3` | `84` | `0.8815` | `0.7024` | `0.9643` | `0.4167` |
| MVC | `4` | `84` | `0.8668` | `0.7024` | `0.9524` | `0.1190` |

The expected result is visible for MaxCut: deeper QAOA improves average decoded quality. The unexpected
or cautionary part is the optimizer-success collapse at higher depth. MaxCut `p = 4` had the best mean
optimality but only `0.3235` optimizer success. The report should therefore say that depth helped decoded
quality under the configured budget, but did not make optimization easier.

For MVC, the depth result is stronger from `p = 1` to `p = 3`: feasibility increases from `0.6905` to
`0.9643`, and mean optimality rises from `0.5821` to `0.8815`. This supports the theoretical idea that
additional QAOA layers can move probability mass toward feasible cover states. But `p = 4` does not
continue the improvement, so the larger parameter space likely offsets some expressivity gains.

Initialization also differed by problem. In the main campaign, MaxCut interpolation and random starts were
nearly tied (`0.9207` vs `0.9190`). For MVC, random starts were better on average (`0.7964` vs `0.7478`)
and had higher feasibility (`0.8964` vs `0.8571`). This supports the first final benchmark's warning that
interpolation is not universally safe for penalty-constrained QUBOs.

## VQE Ansatz And Depth

The VQE results show that ansatz structure matters more for MVC than for MaxCut.

| Problem | Ansatz | Runs | Mean optimality | Quality rate | Feasibility | Optimizer success |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| MaxCut | hardware-efficient | `204` | `0.9589` | `0.5686` | `1.0000` | low |
| MaxCut | problem-aware | `204` | `0.9768` | `0.7255` | `1.0000` | low |
| MVC | hardware-efficient | `168` | `0.7793` | `0.5714` | `0.8393` | low |
| MVC | problem-aware | `168` | `0.9089` | `0.5893` | `1.0000` | low |

Problem-aware VQE was better overall, especially on MVC. The feasibility gap is important:
hardware-efficient VQE had MVC feasibility `0.8393`, while problem-aware VQE had MVC feasibility
`1.0000`. This is good evidence that using the Ising coupling structure in the ansatz can help constrained
problems, at least on these small instances.

Depth did not have a simple monotonic effect. For MaxCut, problem-aware depth 1 already reached mean
optimality `0.9828`, while depth 2 and depth 3 were slightly lower. For MVC, problem-aware depth 2 was
best (`0.9259`), while depth 3 was similar but not better (`0.9199`). Hardware-efficient depth 3 was worse
on MVC (`0.7297`) than depths 1 and 2. This is theoretically reasonable: deeper ansätze are more
expressive, but they also increase the optimization dimension and can make COBYLA's fixed budget less
effective.

## Backend Campaign

The backend campaign ran `147` total runs over `7` representative cases. It included harder cases than the
first backend benchmark, including weighted MaxCut and random MVC cases up to 10 variables.

| Solver | Backend | Runs | Mean optimality | Quality rate | Feasibility | Optimizer success | Runtime (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| QAOA | statevector | `14` | `0.8901` | `0.5714` | `1.0000` | `0.7143` | `0.2911` |
| QAOA | shot-based | `28` | `0.8764` | `0.5357` | `1.0000` | `1.0000` | `0.1008` |
| QAOA | noisy | `28` | `0.8494` | `0.5714` | `0.9643` | `1.0000` | `3.9282` |
| VQE | statevector | `14` | `0.9779` | `0.7857` | `1.0000` | `0.0000` | `0.4747` |
| VQE | shot-based | `28` | `0.9281` | `0.6071` | `1.0000` | `0.6429` | `0.4493` |
| VQE | noisy | `28` | `0.8833` | `0.5357` | `1.0000` | `0.6429` | `17.2031` |

The expected result is the runtime cost of noisy simulation. QAOA noisy runtime averaged `3.9282 s`,
compared with `0.2911 s` statevector. VQE noisy runtime averaged `17.2031 s`, far above both statevector
and shot-based VQE.

The shot-count effect is visible but not definitive. For QAOA, `4096`-shot runs had mean optimality
`0.8987`, higher than `0.8540` at `1024` shots. For VQE, `4096` shots reached `0.9482`, higher than
`0.9080` at `1024` shots. This is consistent with lower sampling error at higher shot count, but it is
not conclusive because optimizer paths are stochastic and the sample size is still small.

Noisy results degraded expectation energy and runtime, but did not uniformly destroy decoded quality. This
is also expected at this scale. These are simulated Aer noise results, not physical-device results, and
they should be reported as backend-sensitivity diagnostics rather than hardware evidence.

## QAOA Initialization Studies

The separate initialization studies used five representative cases and expanded QAOA to `p = 5` with
interpolation, warm-start, and eight random trials per depth.

| Case | Exact objective | Best mean expectation result | Decoded-quality note |
| --- | ---: | --- | --- |
| `maxcut-er8-seed11` | `10` | warm-start `p = 5`, `E = -9.6635` | warm-start decoded optimum at all depths |
| `maxcut-weighted-er8-seed17` | `23` | warm-start `p = 4`, `E = -18.7212` | weighted case needed depth for optimum |
| `maxcut-weighted-er10-seed17` | `51` | warm-start `p = 5`, `E = -46.5846` | warm-start decoded optimum from `p = 2` onward |
| `mvc-er8-seed11` | `3` | interpolation `p = 5`, `E = 4.8565` | MVC ratios are raw and not feasibility-adjusted |
| `mvc-er10-seed11` | `5` | warm-start `p = 5`, `E = 6.8224` | MVC raw ratios need careful interpretation |

For MaxCut, warm-start is the clearest winner. It consistently improved expectation energy with depth and
often reached the exact decoded objective. This supports the theoretical motivation for warm-starting:
lower-depth optimized parameters provide a better starting point than isolated random restarts at higher
depth.

For weighted MaxCut, depth matters more than on the easier unweighted case. The 8-node weighted case had
interpolation `p = 1` approximation `0.6087`, but warm-start reached exact decoded quality at depths `2`,
`3`, and `4`. The 10-node weighted case showed an even stronger warm-start signal, reaching exact decoded
quality from `p = 2` onward and the best expectation at `p = 5`.

The MVC initialization studies are useful but less clean. The current initialization workflow reports a
raw `objective / optimum` approximation-style value, which is natural for MaxCut but not minimization- or
feasibility-aware for MVC. Therefore, MVC initialization tables should be used mainly for expectation
energy, optimizer behavior, and qualitative initialization sensitivity. Feasibility-adjusted MVC claims
should come from the main campaign.

## Landscape And Gradient Studies

The landscape studies ran four one-problem analyses. Each used a `61 x 61` QAOA `p = 1` grid, `20`
multi-start QAOA runs, `50` QAOA gradient samples, and `50` VQE gradient samples.

| Case | Exact objective | Best grid energy | Dominant probability | Multi-start best objective | Mean QAOA gradient | Mean VQE gradient |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `maxcut-er8-seed11` | `10` | `-7.2741` | `0.0417` | `10` | `2.4233` | `0.8274` |
| `maxcut-weighted-er8-seed17` | `23` | `-17.8340` | `0.0326` | `23` | `9.3298` | `2.9408` |
| `mvc-er8-seed11` | `3` | `9.0000` | `0.0483` | diagnostic only | `6.8951` | `1.2436` |
| `mvc-cycle8` | `4` | `7.6195` | `0.0198` | diagnostic only | `3.7142` | `1.0929` |

The MaxCut landscape results are useful and internally consistent. The best grid dominant bitstring had
the exact optimum energy for both MaxCut cases, and multi-start optimization also found the exact decoded
objective. The weighted landscape had much larger QAOA gradients than the unweighted ER case, which is
consistent with the larger weighted energy scale and sharper objective differences.

The MVC landscape results are exploratory rather than conclusive. The landscape workflow records dominant
energies and expectation values correctly, but some summary fields are not minimization-aware in the same
way the benchmark campaign is. Therefore, MVC landscape plots are still useful for visualizing parameter
sensitivity and gradient scales, but MVC feasibility and optimality claims should come from the campaign
tables.

The gradient statistics do not demonstrate barren plateaus. The instances are small, and all mean gradient
norms are visibly nonzero. The useful conclusion is narrower: on these selected cases, QAOA had larger and
more variable sampled finite-difference gradients than the hardware-efficient VQE ansatz.

## Expected Results

Several outcomes match theory and expectations.

Brute force found every exact optimum. This validates the exact-reference setup and confirms that the
optimality ratios are meaningful.

Increasing QAOA depth improved MaxCut results. The monotonic MaxCut mean optimality sequence
`0.8542 -> 0.9208 -> 0.9383 -> 0.9638` from `p = 1` to `p = 4` is the cleanest expected result.

Weighted MaxCut and random MVC were harder than simple cycles and paths. This was expected because random
structure, weights, and penalty terms create more complex landscapes than simple regular graphs.

Noisy backend simulation was slower. This was expected because Aer noisy sampling is more expensive than
statevector expectation evaluation or seeded ideal shot sampling.

Warm-start QAOA improved high-depth MaxCut initialization. This matches the theory that optimized
lower-depth parameters can give useful structure to higher-depth starts.

## Unexpected Or Cautionary Results

The strongest cautionary result is the gap between optimizer status and decoded solution quality. Many
runs decoded optimal or near-optimal bitstrings even when COBYLA reported failure. Conversely, some QAOA
MVC interpolation runs reported optimizer success while decoding infeasible bitstrings. Optimizer success
is therefore a diagnostic, not a solution-quality metric.

Shallow interpolation failed badly on several MVC cases. The worst rows include MVC random/path cases where
`qaoa_interpolation_p1` had mean optimality `0.0000`, feasibility `0.0000`, and optimizer success
`1.0000`. This is one of the most important results for the report because it shows that a smooth
initialization heuristic can optimize the penalty Hamiltonian while still placing dominant probability on
infeasible covers.

OpenJij performed extremely well overall, but its aggregate behavior is not uniformly simple. It was
near-perfect on MVC and random graph groups, yet weaker on cycle aggregates. This should not be
overinterpreted without a targeted OpenJij parameter sweep.

VQE depth was not monotonic. Deeper VQE increased expressivity, but depth 3 did not reliably improve
decoded quality and often hit the maximum evaluation budget. This is consistent with larger parameter
spaces being harder for a local derivative-free optimizer.

## What Is Conclusive

It is reasonable to claim that the repository now has a complete reproducible benchmark pipeline for QUBO
modeling, exact references, OpenJij, QAOA, VQE, backend comparison, initialization analysis, and landscape
analysis.

It is reasonable to claim that the large benchmark gives stronger evidence than the first final benchmark.
The run count increased from hundreds to thousands, the problem set includes more seeds and sizes, and the
harder cases reveal nontrivial solver differences.

It is reasonable to claim that QAOA depth helps MaxCut decoded quality under this configuration, while
MVC requires feasibility-aware interpretation.

It is reasonable to claim that problem-aware VQE is more reliable than hardware-efficient VQE on MVC in
this dataset, especially because it preserved feasibility at `1.0000` in the aggregate.

## What Is Not Conclusive

The benchmark does not show quantum advantage. All instances are small enough for exact brute-force
references, and brute force remains fast at these sizes.

The benchmark does not prove that VQE is generally better than QAOA. VQE had higher mean optimality in the
main campaign, but the comparison depends on ansatz family, depth, optimizer budget, problem family, and
the distinction between expectation energy and decoded bitstrings.

The backend campaign does not establish hardware behavior. Shot-based mode is finite sampling from ideal
probabilities, and noisy mode is simulated Aer noise.

The gradient study does not establish barren plateaus. It is a small finite-difference trainability
snapshot with nonzero gradients.

The MVC initialization and MVC landscape summaries are not the best source for final feasibility claims.
Use them as diagnostic views, and use the main campaign for feasibility-adjusted MVC results.

## Recommended Use In The Final Report

Use the main campaign as the central results section. The best tables are
`solver_family_aggregates.csv`, `problem_size_aggregates.csv`, `qaoa_depth_aggregates.csv`, and
`vqe_depth_aggregates.csv`.

Use the backend campaign as a focused subsection on simulation mode. Emphasize runtime and expectation
energy differences, and discuss shot-count sensitivity carefully.

Use the QAOA initialization studies to support a warm-start discussion, especially on MaxCut and weighted
MaxCut. State clearly that MVC initialization ratios are diagnostic unless feasibility-adjusted.

Use the landscape studies for visual explanation. The MaxCut heatmaps and multi-start plots are the best
figures for explaining the relation between smooth expectation landscapes and discrete decoded objective
quality.

The final report should present the large benchmark as a controlled exact-reference empirical study. Its
strength is not scale or hardware realism; its strength is that it exposes meaningful solver behavior on a
transparent, reproducible QUBO pipeline.
