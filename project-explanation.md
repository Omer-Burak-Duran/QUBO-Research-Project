# Project Explanation

## 1. Project identity

This project is a research-oriented Python framework for **QUBO modeling**, **variational quantum optimization**, and **optimization-landscape analysis**.

Its job is not only to “run QAOA or VQE on some problems.” Its real job is to create a reusable research system where:

1. a combinatorial optimization problem can be encoded into QUBO in a transparent way,
2. that QUBO can be converted into an Ising / cost Hamiltonian form,
3. multiple solvers can be applied to the same encoded problem,
4. outputs can be compared fairly, and
5. the optimization behavior itself can be studied, not just the final answer.

This matches the scope of our study: mastering QUBO modeling, implementing QAOA and VQE, and analyzing convergence and barren-plateau-like behavior.

---

## 2. Core purposes of the project

### Purpose A: Master QUBO modeling

QUBO is the central modeling layer. A QUBO problem has the form

[min/max ; x^T Q x]

with binary decision variables. It is attractive because many constrained combinatorial problems can be rewritten into this unconstrained binary form using penalty terms. That modeling flexibility is one of the main reasons QUBO is widely used in quantum optimization work.

In this project, QUBO is not just an intermediate object. It is the **canonical representation** of each benchmark problem.

### Purpose B: Apply QAOA and VQE to the same encoded problems

QAOA and VQE are both hybrid quantum-classical variational methods. QAOA is directly motivated by combinatorial optimization and uses alternating cost and mixer evolutions. VQE uses a parameterized ansatz and classical optimization of measured expectation values. The shared hybrid structure makes them comparable inside one framework.

### Purpose C: Study optimization landscapes

The project should not stop at “best value found.” It should let us inspect:

- optimizer trajectories,
- dependence on initialization,
- parameter sensitivity,
- gradient magnitude statistics,
- local minima structure,
- approximation ratio vs depth,
- convergence behavior under noise or finite shots.

This matters because QAOA performance beyond very small depth depends strongly on outer-loop optimization, and constructive initialization strategies can greatly change practical performance.

---

## 3. Scope for the first full version

The first major version of the project should include:

- QUBO modeling of **MaxCut**,
- QUBO modeling of **Minimum Vertex Cover**,
- QUBO modeling of **Traveling Salesman Problem (TSP)**,
- **QAOA** on these benchmark problems,
- **VQE** on the corresponding cost Hamiltonians,
- classical baselines,
- plotting and experiment logging,
- small-scale landscape analysis.

This is a good scope because the three problems have different modeling character:

- **MaxCut** is the cleanest starting point and almost “native” to QUBO.
- **Minimum Vertex Cover** introduces explicit constraint penalties and is good for learning penalty design.
- **TSP** is much heavier and tests whether the software stays modular when encodings become larger and more structured. Lucas’ Ising formulation for TSP uses order variables and adds a weighted tour term on top of Hamiltonian-cycle constraints, which makes it a good stress test for the framework.

This scope is also expandable. If later we add another problem, for example **Facility Location**, we should not need to redesign the project. We should only add:

- one new problem module,
- one encoder,
- one decoder,
- one benchmark config.

That is the definition of good modularity here.

---

## 4. Design philosophy

The project should follow five principles.

### 4.1 One canonical internal representation

All benchmark problems should become a common internal object, for example:

- `QUBOModel`
- `IsingModel`
- `ProblemInstance`
- `DecodedSolution`

This is the most important design choice.

If every solver accepts a different input type, the project becomes messy very fast. If all problems first become `QUBOModel`, then everything downstream becomes cleaner:

- classical QUBO solvers consume the QUBO directly,
- quantum modules convert QUBO to Ising / Pauli form,
- analysis modules compare methods on the same instance.

### 4.2 Separate modeling from solving

A problem encoder should not know whether the downstream solver is QAOA, VQE, OpenJij, brute force, or ILP.

The encoder’s responsibilities are:

- define binary variables,
- produce the Q matrix and constant offset,
- record penalty parameters,
- provide a decode method from bitstring to semantic solution,
- provide a feasibility checker and objective evaluator.

Everything else belongs elsewhere.

### 4.3 Reproducibility is a first-class feature

Every experiment should be reproducible through:

- saved config files,
- fixed random seeds,
- stored optimizer settings,
- saved instance data,
- logged software/backend information.

This is a research project, so reproducibility is not optional.

### 4.4 Transparent mathematics over magic wrappers

Libraries like `pyqubo` are useful, but they can hide too much when we are still learning and validating formulations. Since one of our main goals is to **master QUBO modeling**, the final framework should keep the mathematics visible.

So the recommendation is:

- use **manual formulations** as the main implementation,
- use `pyqubo` only as an optional validation or prototyping tool.

### 4.5 Exact small-scale validation before larger-scale experiments

Every new encoder should first be tested on tiny instances where we can verify:

- feasibility by inspection,
- objective value by hand or brute force,
- QUBO energy equals expected cost plus penalties,
- QUBO-to-Ising conversion preserves argmin / argmax.

This will save us from subtle bugs later.

---

## 5. Recommended tech stack

## 5.1 Core numerical stack

### `numpy`
Use for arrays, Q matrices, bitstring operations, energy evaluation, and parameter handling.

### `scipy`
Use for:

- optimizers,
- sparse matrices,
- small exact diagonalization,
- linear algebra utilities.

This will be especially useful for exact small-system Hamiltonian analysis and for gradient or Hessian approximations.

### `matplotlib`
Use for all standard research plots:

- energy vs iteration,
- approximation ratio vs depth,
- parameter trajectories,
- heatmaps,
- landscape slices,
- gradient-norm distributions.

### `pandas`
Useful for experiment tables, run summaries, and easy export to CSV.

### `networkx`
Strongly recommended for graph-based benchmark problems. It simplifies:

- graph creation,
- random instance generation,
- visualization,
- access to adjacency and edge weights.

For MaxCut, Minimum Vertex Cover, and TSP instances, this is very practical.

## 5.2 Quantum stack

### `qiskit`
Recommended for:

- circuit construction,
- QAOA and VQE circuits,
- parameter binding,
- statevector simulation,
- shot-based simulation through Aer,
- Hamiltonian / Pauli operator handling.

Use Qiskit mainly at the **algorithm/backend layer**, not the modeling layer.

### `qiskit-aer`
Use for:

- exact statevector simulation,
- shot-based simulator,
- optional noise models later.

### Optional: `qiskit-algorithms`
We may use higher-level QAOA/VQE utilities for quick validation, but for research transparency it is recommended that we implement our own experiment wrapper around lower-level primitives.

Reason: once we want custom logging, landscape scans, custom initializations, or fair side-by-side comparisons, black-box high-level classes become limiting.

## 5.3 Classical optimization / baseline stack

### `openjij`
Good for:

- simulated annealing,
- simulated quantum annealing,
- sampling QUBO / Ising formulations.

This is valuable because it gives us a non-variational baseline that still works directly on the QUBO/Ising side.

### `PuLP` or `OR-Tools`
Use for exact or near-exact classical benchmarks where possible.

- `PuLP` is simple and open.
- `OR-Tools` is also practical.
- `Gurobi` can be supported as an optional high-performance backend if available.

The important design choice is not which solver wins. The important choice is to implement a **solver interface** so the project does not depend on one specific classical package.

## 5.4 Software engineering stack

### `pytest`
For unit and integration tests.

### `pyyaml`
For experiment configs.

### `dataclasses` or `pydantic`
Can use `dataclasses` if we want lightweight typed containers.
Can use `pydantic` if we want stronger validation.

For a research codebase, `dataclasses` are usually enough unless config complexity grows a lot.

### `pathlib`
Use for robust file and directory handling.

---

## 6. What should be implemented manually and what should use libraries

### Implement manually

These are central to our learning and research goals:

- QUBO encodings for each benchmark problem,
- QUBO to Ising conversion,
- solution decoding,
- feasibility checking,
- energy evaluation,
- experiment runner,
- logging and plotting,
- landscape analysis utilities,
- small custom QAOA/VQE wrappers.

### Use libraries for convenience

These are support layers, not the research contribution itself:

- graph utilities (`networkx`),
- simulator backends (`qiskit-aer`),
- classical optimizers (`scipy.optimize`),
- classical samplers (`openjij`),
- exact classical solvers (`PuLP`, `OR-Tools`, optional `Gurobi`).

This division keeps the project educational, auditable, and still practical.

---

## 7. Recommended project structure

```text
project-root/
├── README.md
├── pyproject.toml
├── configs/
│   ├── base.yaml
│   ├── problems/
│   │   ├── maxcut.yaml
│   │   ├── min_vertex_cover.yaml
│   │   └── tsp.yaml
│   └── experiments/
│       ├── qaoa_sweep.yaml
│       ├── vqe_sweep.yaml
│       └── landscape.yaml
├── data/
│   ├── raw/
│   ├── instances/
│   └── results/
├── src/
│   └── qubo_vqa/
│       ├── core/
│       │   ├── qubo.py
│       │   ├── ising.py
│       │   ├── pauli.py
│       │   ├── result.py
│       │   └── types.py
│       ├── problems/
│       │   ├── base.py
│       │   ├── maxcut.py
│       │   ├── min_vertex_cover.py
│       │   ├── tsp.py
│       │   └── generators.py
│       ├── converters/
│       │   ├── qubo_to_ising.py
│       │   └── validation.py
│       ├── solvers/
│       │   ├── classical/
│       │   │   ├── brute_force.py
│       │   │   ├── ilp.py
│       │   │   └── openjij_solver.py
│       │   └── quantum/
│       │       ├── qaoa.py
│       │       ├── vqe.py
│       │       ├── ansatz.py
│       │       ├── mixers.py
│       │       ├── estimators.py
│       │       ├── backends.py
│       │       └── initialization.py
│       ├── experiments/
│       │   ├── runner.py
│       │   ├── benchmark.py
│       │   ├── sweeps.py
│       │   └── logging.py
│       ├── analysis/
│       │   ├── metrics.py
│       │   ├── plots.py
│       │   ├── landscape.py
│       │   └── barren_plateau.py
│       └── utils/
│           ├── config.py
│           ├── random.py
│           ├── io.py
│           └── timing.py
└── tests/
    ├── test_qubo_models.py
    ├── test_converters.py
    ├── test_classical_solvers.py
    ├── test_qaoa_small.py
    └── test_vqe_small.py
```

This structure separates concerns in a way that supports future growth.

---

## 8. Core abstractions

## 8.1 `ProblemInstance`

Represents a concrete instance such as:

- a specific graph for MaxCut,
- a specific graph for Minimum Vertex Cover,
- a specific weighted graph for TSP.

It should contain raw problem data only.

## 8.2 `QUBOModel`

This is the canonical encoded object.

Suggested fields:

- `Q`: quadratic matrix,
- `offset`: constant term,
- `sense`: min or max,
- `var_names`: mapping index to semantic variable,
- `metadata`: penalty strengths, source problem, instance id.

Methods should include:

- `energy(bitstring)`,
- `to_ising()`,
- `num_variables()`.

## 8.3 `IsingModel`

Represents the quantum cost Hamiltonian in Ising form.

Suggested fields:

- local fields `h`,
- couplings `J`,
- constant offset,
- Pauli operator representation for Qiskit.

## 8.4 `DecodedSolution`

Maps a raw bitstring back to meaning:

- cut partition,
- chosen cover vertices,
- tour order.

It should also report:

- feasibility,
- original objective value,
- penalty contribution,
- total QUBO energy.

## 8.5 `SolverResult`

A standard result object should make comparison easy.

Suggested fields:

- best bitstring,
- best energy,
- decoded solution,
- runtime,
- iteration history,
- shot count,
- seed,
- backend info,
- extra metrics.

If every solver returns this same structure, analysis becomes much easier.

---

## 9. Problem encoding strategy

## 9.1 MaxCut

MaxCut is the best first problem because the formulation is clean and direct. In QUBO form, maximizing cut edges can be written with terms of the form

[x_i + x_j - 2 x_i x_j]

summed over graph edges.

Why start here:

- small formulation effort,
- easy to visualize,
- natural QAOA benchmark,
- many papers study it,
- easy to validate against brute force for small graphs.

## 9.2 Minimum Vertex Cover

This is our first serious penalty-modeling problem.

A common binary encoding is:

- `x_i = 1` if vertex `i` is selected.

Then:

- minimize the number of selected vertices,
- penalize every uncovered edge.

## 9.3 TSP

TSP is optional and it should be added only after the first two problems are working.

A standard encoding uses binary assignment variables like `x[v, j]`, meaning city `v` is placed at tour position `j`. The formulation includes:

- one city per position,
- one position per city,
- weighted transitions between consecutive positions.

Lucas’ Ising construction uses exactly this ordering-style representation and notes the variable cost scaling like ((N-1)^2) after a simple symmetry fixing.

Why TSP should come later:

- it has larger variable count,
- more penalties,
- more fragile decoding,
- more room for silent bugs.

---

## 10. Quantum algorithm layer

## 10.1 QAOA design

QAOA is naturally matched to combinatorial optimization. The problem Hamiltonian is the Ising/QUBO-derived cost Hamiltonian, and the mixer is usually a transverse-field type operator. The original QAOA paper defines a p-level alternating application of cost and mixer unitaries, with approximation quality improving as p increases.

For our framework, QAOA should support:

- arbitrary cost Hamiltonian from encoded QUBO,
- configurable depth `p`,
- exact-statevector evaluation,
- shot-based evaluation,
- several optimizers,
- pluggable initializations.

### Recommended QAOA options

- **Backend mode 1:** exact statevector for development,
- **Backend mode 2:** shot-based simulator for realistic variational behavior,
- **Optimizers:** COBYLA, Nelder-Mead, SPSA, L-BFGS-B,
- **Initialization:** random, warm-start, interpolation, Fourier-inspired heuristics.

The Zhou et al. QAOA paper is especially relevant here because it shows that parameter initialization is not a minor detail. It can change optimization cost dramatically, and heuristic warm-start strategies can scale much better than repeated random restarts.

## 10.2 VQE design

VQE is less problem-specific than QAOA, which is exactly why it is valuable in our project. It gives us a second variational algorithm with a different ansatz philosophy.

The Peruzzo et al. VQE paper describes the hybrid pattern clearly:

- quantum processor prepares parameterized states,
- expectation values of Hamiltonian terms are measured,
- a classical optimizer updates parameters.

For combinatorial optimization, our VQE implementation should support at least two ansatz families:

### A. Hardware-efficient ansatz

Useful because it is simple and backend-friendly.

### B. Problem-aware ansatz

Useful because it may reveal whether structure helps optimization and whether unstructured ansätze behave worse in the landscape.

This is important for our landscape goals. A structured ansatz and an unstructured ansatz may show very different trainability.

---

## 11. Classical baselines

Our project needs strong classical baselines for two reasons:

1. to verify correctness,
2. to interpret quantum results honestly.

The baseline set should include:

### A. Brute force
For tiny instances only.

Use this for truth.

### B. Exact classical optimization
Use ILP / MILP or another exact solver when feasible.

### C. OpenJij sampling
Use simulated annealing and simulated quantum annealing as additional baselines.

### D. Optional heuristic baseline
For example, a greedy or local-search baseline for quick sanity checks.

Do not compare QAOA or VQE only against each other. Compare them against the best classical method available at that size.

---

## 12. Experiment workflow

Every benchmark run should follow the same pipeline:

1. Generate or load problem instance.
2. Encode instance to `QUBOModel`.
3. Validate energy on tiny test bitstrings.
4. Convert QUBO to `IsingModel`.
5. Run classical baselines.
6. Run QAOA.
7. Run VQE.
8. Decode best bitstrings.
9. Compute metrics.
10. Save plots, tables, configs, and raw histories.

This uniform pipeline is what turns a collection of scripts into a research framework.

---

## 13. Metrics that should be recorded

For every run, record at least:

- best energy,
- best decoded objective value,
- feasibility rate,
- approximation ratio,
- optimizer iterations,
- runtime,
- number of function evaluations,
- number of shots,
- random seed,
- depth `p` or ansatz depth,
- backend type,
- ground-state overlap or exact optimum gap when available.

For QAOA specifically, also record:

- parameter vector,
- initialization strategy,
- cost per iteration,
- final sampling distribution if shot-based.

For VQE specifically, also record:

- ansatz type,
- parameter count,
- entangling layer count.

---

## 14. Landscape analysis plan

This project’s third pillar requires dedicated analysis code, not just extra plots.

## 14.1 For very small systems

For small MaxCut instances and low depth QAOA:

- build full parameter grids,
- plot energy landscapes,
- plot approximation ratio landscapes,
- compare local minima structure.

For `p = 1`, two parameters are easy to scan fully.
For `p = 2`, use slices or contour projections.

## 14.2 For larger depths

Full grids are impossible, so use:

- optimizer trajectory plots,
- random-direction line scans,
- perturbation sensitivity around found minima,
- multi-start clustering of final parameters.

## 14.3 Barren-plateau-style analysis

Do not begin with abstract claims. Make it empirical.

For both QAOA and VQE, measure:

- gradient norm statistics,
- finite-difference slope magnitudes,
- variance of objective change under small parameter perturbations,
- how these scale with qubit count and depth.

A useful hypothesis to test is whether a structured ansatz such as shallow QAOA remains more trainable than a more generic VQE ansatz on the same problem family.

## 14.4 Adiabatic / non-adiabatic interpretation

The QAOA performance paper shows that QAOA can exploit non-adiabatic mechanisms and can outperform adiabatic annealing on hard instances with small spectral gaps.

So one useful interpretation layer in our project is:

- compare QAOA depth growth to annealing-style intuition,
- examine whether optimized parameter schedules look smooth or not,
- inspect whether good solutions require clearly non-adiabatic behavior.

---

## 15. Testing strategy

A research codebase without tests becomes unreliable very quickly.

We should include the following test categories.

### 15.1 Encoding tests

For each problem:

- create tiny instances,
- evaluate all bitstrings,
- confirm that the best QUBO solution matches the known classical optimum.

### 15.2 Converter tests

Check that QUBO and Ising energies differ only by known affine transformation.

### 15.3 Decoder tests

A bitstring should decode to the correct semantic object and feasibility status.

### 15.4 Solver sanity tests

For tiny instances:

- QAOA with statevector backend should improve over naive random sampling,
- VQE should recover the ground state on very small Hamiltonians,
- brute force should match exact diagonalization where appropriate.

### 15.5 Reproducibility tests

With a fixed seed and same config, repeated runs should match to expected tolerance.

---

## 16. Why this architecture is good for future extensions

Suppose later we add another problem, for example Facility Location.

With the architecture above, we do **not** touch:

- QAOA core,
- VQE core,
- plotting core,
- experiment runner,
- logging layer,
- baseline solver interfaces.

We only add:

- `problems/facility_location.py`,
- config files,
- a few tests,
- maybe one instance generator.

That is exactly the kind of minimal-change extensibility we want.

---

## 17. Recommended implementation order

Do not build everything at once.

Build in this order:

1. repository skeleton,
2. QUBO core classes,
3. MaxCut encoder,
4. brute force baseline,
5. QUBO to Ising converter,
6. QAOA exact simulator,
7. plotting and logging,
8. Minimum Vertex Cover encoder,
9. VQE exact simulator,
10. shot-based experiments,
11. landscape modules.

This order keeps the difficulty increasing gradually.

---

## 18. Final recommendation

The best version of this project is **not** the one with the most libraries. It is the one with the clearest boundaries:

- problems are encoded once,
- solvers are interchangeable,
- experiments are config-driven,
- results are reproducible,
- plots and metrics are standardized,
- small instances are always exactly validated.

If we follow that architecture, the project will be:

- clean enough for research,
- modular enough for future benchmark problems,
- transparent enough for learning,
- strong enough to support a serious report or publication-style manuscript.

---