# Modular Python Research Project for QUBO Modeling, QAOA/VQE, and Landscape Analysis

## Context and research objectives

This project aims to unify three tightly coupled research activities into a single, large, reusable Python codebase: (i) principled **QUBO** formulation and validation, (ii) applying **variational quantum algorithms (VQAs)** (specifically **QAOA** and **VQE**) to benchmark QUBO problems, and (iii) systematically probing the **optimization landscape** (trainability, convergence behavior, and barren plateaus) under different ansätze, depths, optimizers, and noise models.

QUBO is a particularly practical “hub representation” because it expresses a broad family of discrete optimization problems as minimizing a quadratic function of binary variables—often written as an upper-triangular matrix (Q) over binary decision vector (x), and it is closely connected to Ising formulations that map naturally onto qubit Z-type Hamiltonians.

On the algorithm side, QAOA (introduced as an approximate combinatorial optimizer via alternating “cost” and “mixer” unitaries) and VQE (introduced as a hybrid variational method for finding minimum eigenvalues) are both canonical VQAs for NISQ-era experiments, and both reduce to minimizing expectation values of problem Hamiltonians with respect to a parametrized quantum circuit.

On the landscape side, the “barren plateau” phenomenon (exponentially vanishing gradients in broad classes of parametrized circuits) poses a core risk for scalability and motivates a design that makes it easy to run controlled experiments across circuit depth, problem size, cost locality, and noise.

## Core technical choices and tech stack

A clean research codebase benefits from two design principles: (a) **standard internal representations** for problems/Hamiltonians/results, and (b) **separation of concerns** between modeling, solvers, experiment orchestration, and analysis. This aligns well with modern Python packaging practices that recommend the `src/` layout to avoid accidental imports from the working directory and to ensure that tests exercise the installed package behavior.

A robust stack for our goals (modeling → solving → logging → visualization) is:

**Scientific core**

- **NumPy** for array computing and fast numerics (energies, penalties, sampling post-processing).
- **SciPy** for optimization (e.g., `scipy.optimize.minimize` methods such as COBYLA, Nelder-Mead, etc.) and for providing a stable baseline optimizer interface if we want to compare against quantum-specific optimizers.
- **pandas** (optional but strongly useful) for storing results as structured tables and enabling quick aggregations across seeds/instances/depths.
- **Matplotlib** for static plots (landscape heatmaps, convergence curves, approximation ratios vs depth, gradient variance vs qubits).

**Problem instances and benchmarks**

- **NetworkX** for graph creation/manipulation (Max-Cut, Vertex Cover), including built-in graph generators.

**QUBO modeling and interop**

- **PyQUBO** to build QUBO/Ising models from symbolic-like expressions, including placeholders for tunable penalty strengths (very helpful when we want to sweep penalty parameters without recompiling the whole model).
- A **Binary Quadratic Model (BQM)** abstraction is valuable as an interop layer because it can represent both QUBO and Ising models and can convert between these formats programmatically (and is widely used in QUBO toolchains).
- **dimod** is a common BQM/QUBO/Ising API with functions to convert to QUBO or Ising formats (useful both for correctness checks and for connecting to classical samplers).
- **Qiskit Optimization** can be leveraged in two ways: (i) as an automated converter from constrained quadratic programs into QUBO (with a penalty factor), and (ii) as a translator to an Ising Hamiltonian mapped to qubits. This is extremely convenient both as a reference implementation and as a validation tool for our own hand-derived QUBOs.

**Classical baselines for QUBO**

- **OpenJij** offers simulated annealing / simulated quantum annealing style heuristics for Ising/QUBO models and is useful as a baseline and for quick “sanity-check” solves of medium-size instances.

**Quantum algorithms and simulation**

- **Qiskit primitives (Sampler/Estimator)** provide the modern abstraction for sampling bitstrings and estimating expectation values of observables; V2 primitives define base interfaces for samplers/estimators.
- **Qiskit Aer** is the high-performance simulator with noise modeling, and it also provides Aer-based primitive implementations to run exact or noisy simulations (useful for studying noise-induced trainability issues).
- **Qiskit Algorithms** exists as a standalone package; the `qiskit.algorithms` import path is deprecated and the migration rationale is documented (this matters for a long-lived research project).
- The canonical algorithm implementations we you care about (**QAOA** and **VQE**) are available as Qiskit algorithm classes, designed to work with primitives.

**Configuration, reproducibility, and code quality**

- **Hydra** for hierarchical, composable configs and command-line overrides, particularly useful for running many experiments across seeds, depths, optimizers, penalties, and noise models.
- **pytest** for a scalable testing approach, including shared fixtures through `conftest.py`.
- **Ruff** for fast linting and formatting (keeping the codebase consistent as it grows).

A practical environment constraint to keep in mind is Python compatibility: Qiskit’s release notes indicate shifts in minimum supported Python versions over time, and Qiskit documentation notes support for CPython specifically, this makes it safer to standardize our research project on a modern CPython version (for this case we can use version 3.12.10) and pin versions in `pyproject.toml`/lockfiles.

## Reference QUBO formulations for benchmark problems

A key way to “master QUBO modeling” in code is to standardize how we express: **variables**, **objective**, **constraints as penalties**, and **decode/validate** functions. A widely cited compilation of Ising (and therefore QUBO) formulations across many NP-hard problems is Lucas’ reference, which is suitable as a baseline mapping source when implementing Max-Cut and Vertex Cover.

### Max-Cut

QAOA’s original paper already treats Max-Cut as a motivating example, which makes it a natural “first benchmark”: small instances are easy to brute force, and the cost Hamiltonian is a simple sum of pairwise (Z_i, Z_j) interactions after mapping to spins.

Implementation approach:

- Represent the graph as `networkx.Graph` (optionally weighted).  
- Use binary variables (x_i in {0,1}) or spins (s_i in {-1, +1}).  
- Encode the cut indicator per edge in a quadratic form (either directly in QUBO over (x), or as an Ising Hamiltonian over (s)); keep a consistent convention for “minimize vs maximize” (e.g., store a `sense` field and always convert to minimization internally). 
- Provide a `decode(bitstring)->cut_value` method and a deterministic objective evaluator to verify quantum/annealing outputs.

### Minimum Vertex Cover

Vertex Cover has a clean constraint structure: for every edge ((u,v)), at least one endpoint must be selected. In QUBO, constraints are typically enforced by adding penalty terms to the objective so violations are energetically unfavorable, while the objective counts selected vertices. Lucas provides a standard Ising/QUBO-style mapping for covering-type problems (including Vertex Cover), which we can treat as a reference for correctness.

Implementation approach:

- Variables (x_v in {0,1}) indicate whether vertex (v) is in the cover.
- Objective: minimize (sum_v x_v).
- Constraint per edge ((u,v)): (x_u + x_v ge 1), encoded via a quadratic penalty that is zero when the edge is covered and positive when uncovered (this is where we’ll want a tunable penalty coefficient (M) and dataset-specific validation).  
- In code, treat (M) as a first-class config parameter and record whether the best-found bitstring is feasible under the original constraints.

### Traveling Salesman Problem (optional)

TSP is the “stress test” benchmark because the standard QUBO encoding uses (O(n^2)) binary variables (x_{i,t}) (city (i) at tour position (t)) plus penalties to enforce “exactly one city per position” and “each city appears exactly once,” and a quadratic travel-cost coupling between successive positions. These encodings are described in standard QUBO/Ising mapping references, including Lucas.

Implementation approach:

- Load instances from TSPLIB-compatible files via TSPLIB95 and extract the distance matrix.
- Variables (x_{i,t}) with constraints:
  - For each position (t): (sum_i x_{i,t} = 1).
  - For each city (i): (sum_t x_{i,t} = 1).
- Objective term: (sum_{t}sum_{i,j} d_{i,j},x_{i,t}x_{j,t+1}) (wraparound for returning to the start).
- Penalties: squared equality constraints are quadratic and can be generated cleanly with PyQUBO expressions using placeholders for penalty coefficients, enabling sweeps of feasibility strength without rebuilding the model.

### Validation strategy for all three problems

To keep the project research-grade, every problem implementation should ship with three validation layers:

1. **Symbolic/model-level checks**: ensure variable counts, constraint counts, and penalty construction are as expected (unit tests).
2. **Energy equivalence checks**: verify that our internal evaluators agree across representations (QUBO ↔ BQM ↔ Ising), using programmatic conversions where possible.
3. **Ground-truth checks for small instances**: brute force all bitstrings for small (n) (or exact classical solvers) to confirm optimal energies and decode correctness.

A useful “cross-check mode” is to build a model both ways ((a) our hand-derived QUBO (PyQUBO/dimod), and (b) a Qiskit Optimization `QuadraticProgram` converted to QUBO/Ising) then compare energies across random assignments. There are converters and translators designed for this purpose.

## Variational algorithm pipeline for QAOA and VQE

The project should treat QAOA and VQE as two implementations of a more general “variational solver” pipeline:

1. Problem instance → QUBO/BQM/Ising
2. Ising → qubit Hamiltonian (e.g., sum of Pauli terms)
3. Choose ansatz family (QAOA form vs generic VQE ansatz), optimizer, and backend (statevector vs shot-based vs noisy)
4. Optimize parameters and record (trace, best energy, best bitstring distribution, feasibility metrics)

QAOA is defined as alternating applications of a cost operator (derived from the objective) and a mixer operator; the original QAOA proposal describes this alternating-operator structure and studies Max-Cut explicitly. Qiskit’s QAOA class formalizes this in code (with depth/repetitions `reps` and a primitive sampler backend), and Qiskit’s tutorial material demonstrates Max-Cut workflows.

VQE uses the variational principle to minimize the expectation value of a Hamiltonian with respect to a parametrized trial state and is implemented as a hybrid classical-quantum loop; the original VQE work demonstrates the principle and reduced coherence requirements compared to phase estimation.

A modern Qiskit implementation should be built on primitives:

- **Samplers** produce samples from classical output registers of circuits or parameter sweeps.
- **Estimators** compute expectation values of observables with respect to circuit-prepared states (exactly what we need for energy evaluation in VQE and for cost evaluation variants).

Because Qiskit’s algorithms module has been migrated to a standalone package and older import paths are deprecated, a long-lived research project should standardize imports and interfaces around the standalone algorithms package (and primitives V2 where applicable).

### Backends: exact, shot-based, and noisy simulation

For landscape analysis, we typically want at least two backend modes:

- **Exact expectation mode** (statevector or analytic): useful for clean landscapes, debugging, and detecting algorithmic effects without sampling noise.
- **Shot-based mode** (sampling noise): important for realism, especially for optimizer behavior that is sensitive to stochastic objectives.
- **Noisy simulation**: essential for studying noise-induced trainability barriers, which have been theoretically analyzed and can produce barren plateaus under realistic noise models.

Qiskit’s Aer tooling supports building noise models and running noisy simulations, and Qiskit documentation describes using Aer-based primitives for exact and noisy runs.

### Optimizers and gradients as first-class modules

To compare convergence and landscape roughness reliably, treat the optimizer choice as a modular plug-in:

- SciPy provides a unified `minimize` interface with multiple local methods (including derivative-free approaches like Nelder-Mead and constrained-appropriate methods like COBYLA variants), which is useful for controlled optimizer tournaments.
- Qiskit includes optimizer implementations intended for variational algorithms (including **SPSA**, which is widely used in quantum settings because it needs only two objective evaluations per step irrespective of parameter dimension).

For landscape and barren plateau experiments, gradients are often the core metric. Qiskit documents a gradients framework including parameter-shift gradients, and the parameter-shift approach to analytic gradients is described in the literature as a method to estimate derivatives using circuit evaluations.

## Landscape analysis and result interpretation workflow

A “landscape analysis” module should not just plot cost surfaces; it should produce **quantitative metrics** that let us compare:

- trainability (gradient norms/variances vs problem size),
- ruggedness (number of local minima proxies, basin structures, correlation lengths),
- sensitivity (quantum Fisher information / parameter sensitivity),
- convergence behavior (optimizer traces, stagnation detection),
- and robustness to sampling/noise.

### Why barren plateaus shape our experimental design

The original barren plateau result shows that, for a broad class of parametrized circuits, gradients can become exponentially small in qubit count, making optimization intractable beyond small sizes. Subsequent work refines the picture: cost function structure matters (local vs global observables can change scaling even for shallow circuits). Noise can itself induce barren plateaus under certain depth-vs-qubit scaling, making noise modeling central if our goal includes realistic convergence studies. Recent reviews synthesize mitigation directions and clarify which mechanisms create which type of untrainability.

### Concrete landscape experiments that fit our benchmarks

For **QAOA** (especially (p=1) and (p=2)), grid-based landscapes are feasible:

- Evaluate (E(beta,gamma)) on a mesh and produce heatmaps; compute basin statistics.
- Compare weighted vs unweighted Max-Cut graphs, and graph families from NetworkX generators.
Recent work explicitly analyzes QAOA energy landscapes using global optimization/basin-style methods, giving us a literature anchor for what to measure and how to interpret it.

For higher depth (p), full grids become intractable; the project should support:

- **2D/3D slices** through high-dimensional parameter vectors (fix all but a few parameters).
- **Random subspace projections** (project to a low-dimensional affine subspace).
- **Correlation-based analyses** (e.g., cross-instance landscape similarity), which is an active line of work for QAOA optimization strategies.

For **VQE**, landscape analyses can emphasize ansatz choice and locality:

- Compare hardware-efficient ansätze vs problem-inspired ansätze (QAOA-style can also be viewed as a structured, problem-inspired variational form). 
- Compare optimizer behavior under exact expectations vs shot noise vs noise models.

A complementary, practical “failure mode” study is that VQAs can have many traps or problematic optimization structures beyond just barren plateaus; there is literature showing landscapes “swamped with traps,” which justifies recording more than final energies (full trajectories, restarts, and failure labels).

### What to store for real interpretability

To make results reusable and publication-grade, store (at minimum) per run:

- full config snapshot (problem size, seed, penalty strengths, optimizer, ansatz, depth, backend, shots, noise model id),
- energy trace over iterations,
- best-found parameters and energy,
- best decoded solution quality (e.g., cut value, tour length),
- feasibility metrics (constraint violation counts/penalty contribution),
- gradient summary stats if computed (mean/var/max across iterations or across random initializations).

This aligns with the barren plateau literature emphasis on gradient statistics and scaling, and with solver/optimizer comparisons that require full traces, not just endpoints.

## Project milestones and deliverables

The milestones below are designed so that each step produces a working, testable artifact, while keeping the architecture extensible (e.g., adding Facility Location later should mean “add a new `Problem` implementation + tests,” not “edit the whole pipeline”).


| Milestone                       | Scope                                     | Concrete deliverables                                                                                                              | Definition of done                                                                                                                         |
| ------------------------------- | ----------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Repository foundation           | Packaging + structure + developer tooling | `src/` layout, `pyproject.toml`, ruff + pytest + basic CI, logging conventions, minimal CLI entrypoint                             | Can install the package and run `pytest` successfully; imports come from installed package (src layout rationale).                         |
| Core abstractions               | Stable internal APIs                      | `Problem` interface (instance → model → decode), `QuboModel`/`IsingModel` dataclasses, `ResultRecord` schema                       | Type-checked interfaces exist; one toy problem runs end-to-end with dummy solver.                                                          |
| Interop layer                   | Prevent lock-in; enable validation        | BQM adapter (e.g., via dimod), converters QUBO↔Ising, energy evaluators; optional Qiskit Optimization translation cross-check path | Random assignment energy equivalence tests pass; conversion utilities match documented conversions.                                        |
| Benchmark problems v1           | Our initial research set                  | Max-Cut and Min Vertex Cover implementations with instance generators/loaders (NetworkX)                              | Each benchmark has: unit tests, brute-force validation on small sizes, decode correctness checks.                                          |
| Classical baselines             | Sanity + comparative evaluation           | OpenJij sampler baseline; optional dimod sampler baseline; common evaluation metrics across baselines                              | For each benchmark, baseline can solve small instances and produce a comparable result object.                                             |
| Quantum solver core             | QAOA + VQE engines                        | QAOA runner and VQE runner built on primitives; backend abstraction (exact vs shot vs noisy)                                       | Can run (Max-Cut, small graph) with QAOA and VQE and obtain energies + decoded solutions; code uses non-deprecated algorithm import paths. |
| Noisy simulation support        | Trainability under noise                  | Aer primitives path + noise model builder utilities + config hooks                                                                 | A single experiment can be toggled between noiseless and noisy backends; results record noise config.                                      |
| Experiment runner + configs     | Research-scale sweeps                     | Hydra configs for problems/solvers/optimizers; run directory management; result serialization                                      | You can launch parameter sweeps (e.g., 30 seeds × p in {1,2,3}) with CLI overrides; each run logs config + results.                        |
| Landscape analysis module       | Our third research objective              | Grid evaluation for low-dim cases; slice/projection evaluation for higher dim; gradient variance tools (optional parameter-shift)  | Generates: heatmaps/curves + a metrics JSON/CSV; gradient tools work on at least one ansatz/backend.                                       |
| Documentation + reproducibility | Make it reusable and extensible           | API docs + tutorials; “add a new problem” guide; pinned dependency set; reproducible seeds                                         | A new problem can be added by implementing `Problem` + tests; docs explain the pipeline clearly.                                           |


Two implementation notes that reduce future refactors:

- Treat “**problem → (QUBO/BQM/Ising) → Hamiltonian**” as a stable boundary. Our solvers should depend only on the Hamiltonian interface + decoding contract, not on the original problem class. This keeps it easy to add other problems, for example Facility Location Problem, later: implement a new QUBO model and decoder, then reuse the solvers unchanged.
- Treat “**backend/primitives**” as a strategy object. Primitives are explicitly designed as abstractions for sampling and expectation estimation, and Aer provides a path for noisy simulation. Designing around that boundary makes it straightforward to add hardware execution later without rewriting the algorithm code.

