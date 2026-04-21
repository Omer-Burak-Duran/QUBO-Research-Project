# Project Milestones

This document gives a concrete implementation path for the project.

The goal is to make the work sequence practical. Each milestone has:

- **goal**,
- **main tasks**,
- **deliverables**,
- **done criteria**.

The milestones are ordered so that each stage builds on stable earlier pieces.

---

## Milestone 0: Repository foundation

### Goal
Create the project skeleton and make the codebase runnable from day one.

### Main tasks

- Create the repository structure.
- Add `pyproject.toml` or `requirements.txt`.
- Set up `src/` layout.
- Set up `tests/` layout.
- Add a basic `README.md`.
- Add config loading with YAML.
- Add seed control utilities.
- Add a simple experiment output folder structure.

### Deliverables

- working Python environment,
- importable package,
- example config file,
- one placeholder unit test.

### Done criteria

- `pip install -e .` works,
- tests run,
- a dummy experiment can save a config and a result file.

---

## Milestone 1: Core data structures

### Goal
Build the internal objects that all later modules will use.

### Main tasks

- Implement `QUBOModel`.
- Implement `IsingModel`.
- Implement `DecodedSolution`.
- Implement `SolverResult`.
- Implement utility methods:
  - `energy(bitstring)`,
  - dimension / variable count,
  - serialization to JSON-friendly format.

### Deliverables

- core classes in `src/qubo_vqa/core/`.

### Done criteria

- we can construct a tiny QUBO model,
- evaluate energies for given bitstrings,
- save and reload model metadata.

---

## Milestone 2: QUBO to Ising conversion layer

### Goal
Create the translation from classical QUBO form to quantum cost-Hamiltonian form.

### Main tasks

- Implement QUBO to Ising conversion.
- Store local fields, couplings, and offset.
- Add a method to generate a Pauli-operator representation for the quantum layer.
- Add validation tests on tiny systems.

### Deliverables

- `converters/qubo_to_ising.py`,
- converter tests.

### Done criteria

For small examples, the ranking of bitstrings is preserved and the energy relation between QUBO and Ising is verified numerically.

---

## Milestone 3: MaxCut problem module

### Goal
Complete the first full benchmark problem end to end.

### Main tasks

- Implement `MaxCutInstance`.
- Implement random graph generation.
- Implement weighted and unweighted graph support.
- Implement MaxCut QUBO encoder.
- Implement bitstring decoder to partition.
- Implement original objective evaluator.
- Add small visualizations for graphs and cuts.

### Deliverables

- `problems/maxcut.py`,
- test graphs,
- unit tests.

### Done criteria

- tiny graphs can be encoded,
- brute force optimum matches decoded QUBO optimum,
- graph plots and cut plots work.

---

## Milestone 4: Classical truth baseline

### Goal
Establish a trusted baseline before any variational algorithm is added.

### Main tasks

- Implement brute-force solver for tiny problems.
- Optionally implement exact ILP baseline interface.
- Add result comparison utilities.

### Deliverables

- `solvers/classical/brute_force.py`,
- `solvers/classical/ilp.py`.

### Done criteria

- the MaxCut module can be solved exactly for small instances,
- results are returned in the standard `SolverResult` format.

---

## Milestone 5: Experiment runner and logging

### Goal
Standardize how experiments are executed and stored.

### Main tasks

- Implement a config-driven runner.
- Save:
  - config snapshot,
  - runtime info,
  - metrics JSON,
  - CSV histories,
  - plots.
- Add a standard result-folder convention.

### Deliverables

- `experiments/runner.py`,
- `experiments/logging.py`.

### Done criteria

A MaxCut brute-force experiment can be launched from a config file and produces a clean result folder.

---

## Milestone 6: QAOA exact-statevector implementation

### Goal
Implement our first quantum variational solver in the simplest reliable setting.

### Main tasks

- Build cost Hamiltonian from `IsingModel`.
- Implement standard mixer Hamiltonian.
- Implement QAOA circuit builder.
- Implement exact expectation evaluation using statevector simulation.
- Support depth `p` as a parameter.
- Add optimizer hooks:
  - COBYLA,
  - Nelder-Mead,
  - L-BFGS-B.
- Log parameter history and objective history.

### Deliverables

- `solvers/quantum/qaoa.py`,
- `solvers/quantum/mixers.py`,
- `solvers/quantum/backends.py`.

### Done criteria

- QAOA runs on MaxCut small instances,
- objective value improves over iterations,
- exact baseline comparison is available,
- approximation ratio can be reported.

---

## Milestone 7: QAOA initialization strategies

### Goal
Add practical optimization improvements that matter for research quality.

### Main tasks

- Implement random initialization.
- Implement warm-start from lower depth.
- Implement interpolation-based initialization.
- Optionally implement Fourier-inspired initialization.
- Compare convergence quality and runtime.

### Deliverables

- `solvers/quantum/initialization.py`,
- benchmark notebook or script comparing initialization methods.

### Done criteria

We can show, on a small batch of MaxCut instances, how initialization changes final performance or optimization cost.

---

## Milestone 8: Plotting and benchmark metrics

### Goal
Create the standard output figures for the first algorithm.

### Main tasks

- Plot energy vs optimizer iteration.
- Plot approximation ratio vs QAOA depth.
- Plot parameter values vs depth.
- Plot runtime and function evaluation counts.
- Add summary tables across instances.

### Deliverables

- `analysis/metrics.py`,
- `analysis/plots.py`.

### Done criteria

We can run a small benchmark sweep and automatically obtain publication-style plots.

---

## Milestone 9: Minimum Vertex Cover module

### Goal
Add the first explicitly penalty-based constrained problem.

### Main tasks

- Implement `MinimumVertexCoverInstance`.
- Define binary variables for chosen vertices.
- Build penalty for uncovered edges.
- Tune penalty parameter handling.
- Implement decoder and feasibility checker.
- Test against brute force and optional ILP.

### Deliverables

- `problems/min_vertex_cover.py`,
- tests and examples.

### Done criteria

- tiny MVC instances decode correctly,
- QUBO optimum matches classical optimum,
- penalty violations are correctly reported.

---

## Milestone 10: VQE exact-statevector implementation

### Goal
Add the second variational algorithm in a way that enables fair comparison with QAOA.

### Main tasks

- Build a VQE driver that minimizes the expectation of the same cost Hamiltonian.
- Implement at least two ansätze:
  - hardware-efficient,
  - problem-aware or structured.
- Support the same optimizer interface as QAOA when possible.
- Log full history.
- Decode best bitstring from final-state sampling or most likely configuration.

### Deliverables

- `solvers/quantum/vqe.py`,
- `solvers/quantum/ansatz.py`.

### Done criteria

- VQE solves tiny MaxCut and MVC instances,
- results can be compared side by side with QAOA,
- ansatz metadata is logged.

---

## Milestone 11: Shot-based and noisy quantum evaluation

### Goal
Move from idealized exact simulation to a more realistic hybrid-variational setting.

### Main tasks

- Add shot-based expectation estimation.
- Add configurable shot count.
- Compare exact vs shot-based objective noise.
- Add optional simple noise model in Aer.
- Re-test optimizers under noisy objectives.

### Deliverables

- extended backend support,
- comparison plots.

### Done criteria

- the same QAOA and VQE code can run in exact or shot-based mode,
- noise sensitivity can be measured directly.

---

## Milestone 12: Landscape analysis module

### Goal
Turn the project into a real landscape-analysis framework.

### Main tasks

#### For QAOA
- Full grid scan for `p = 1` on small MaxCut instances.
- 2D slices or pairwise scans for `p = 2`.
- Multi-start optimization clustering.
- Parameter trajectory visualization.

#### For VQE
- Low-dimensional ansatz scans where feasible.
- Compare structured and unstructured ansätze.

#### Shared analysis
- Finite-difference gradient norms.
- Sensitivity to random perturbations.
- Objective variance across random initializations.
- Correlation between trainability and problem size / depth.

### Deliverables

- `analysis/landscape.py`,
- `analysis/barren_plateau.py`.

### Done criteria

We can generate at least:

- a QAOA `p=1` landscape heatmap,
- a multi-start convergence plot,
- a gradient-statistics plot for one QAOA setting and one VQE setting.

---

## Milestone 13: OpenJij and additional classical sampling baselines

### Goal
Compare variational quantum methods to classical samplers that operate naturally on QUBO/Ising forms.

### Main tasks

- Add OpenJij interface.
- Run simulated annealing.
- Run simulated quantum annealing if desired.
- Compare energies, runtimes, and solution quality.

### Deliverables

- `solvers/classical/openjij_solver.py`,
- comparative result tables.

### Done criteria

For at least one problem family, we can compare brute force, QAOA, VQE, and OpenJij on the same instance set.

---

## Milestone 14: Full benchmark campaign

### Goal
Generate a complete dataset for the project report or presentation.

### Main tasks

- Select instance-size ranges for MaxCut and MVC.
- Define experiment grids over:
  - problem size,
  - graph family,
  - QAOA depth,
  - VQE ansatz depth,
  - optimizer,
  - initialization strategy,
  - shot count.
- Run batched sweeps.
- Save aggregated CSV summaries.

### Deliverables

- `experiments/sweeps.py`,
- benchmark result folders,
- summary tables.

### Done criteria

We have a clean dataset from which we can make final project plots without rerunning ad hoc scripts.

---

## Milestone 15: Final interpretation layer

### Goal
Translate raw results into research conclusions.

### Main tasks

- Identify which encodings are stable and easy to validate.
- Compare QAOA and VQE fairly by problem and size.
- Evaluate when optimization becomes difficult.
- Interpret whether structured ansätze help.
- Interpret whether parameter initialization changes practical trainability.
- Summarize where landscape flattening or vanishing sensitivity begins to appear.

### Deliverables

- final figures,
- conclusion notes,
- manuscript-ready result summaries.

### Done criteria

We can answer the following clearly:

1. Which benchmark problems were encoded correctly and robustly?
2. How do QAOA and VQE compare on the same encoded problems?
3. What landscape patterns did you observe?
4. What were the main bottlenecks: encoding size, optimizer behavior, shots, or ansatz design?

---

## Recommended execution order in one line

Build in this order:

**foundation → core models → MaxCut → brute force → QAOA → logging/plots → MVC → VQE → shot-based mode → landscape analysis → full benchmark campaign**

---

## Minimum success criteria for the whole project

At the end of the project, the framework should be able to do all of the following:

- encode MaxCut and Minimum Vertex Cover into QUBO,
- convert QUBO into Ising / Pauli cost Hamiltonians,
- solve small instances exactly,
- run QAOA and VQE on the same problem instances,
- compare against classical baselines,
- save reproducible results,
- produce landscape and convergence plots,
- support easy addition of a future problem such as Facility Location.

If all of that works, then the project is not just “some scripts.” It is a serious reusable research platform.
