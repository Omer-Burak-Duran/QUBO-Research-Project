# MIDTERM REPORT DRAFT

## Title Page

- Report title
  - Midterm Report: Variational Quantum Algorithms for Combinatorial Optimization and Modeling
- Name, Course, Semester, Instructor

## 1. Introduction

- Explain the general motivation of the study
  - Many important optimization problems are combinatorial and hard to solve exactly
  - Quantum computing offers alternative ways to represent and attack such problems

- Introduce the central idea of the project
  - translate classical optimization problems into QUBO form
  - convert QUBO to Ising form when needed
  - study QAOA and VQE as candidate variational methods

- State the practical aim of the independent study
  - build understanding from modeling to algorithmic application
  - connect theory to implementation on near-term quantum devices

- State what the report is intended to do
  - summarize theoretical background studied so far
  - document progress already made
  - explain the implementation direction
  - define the plan for the rest of the semester

- End the section with a short report roadmap
  - what the reader will see in the following sections

## 2. Research Objectives

- Present the main objectives as a short numbered list:
  - Learn how benchmark combinatorial optimization problems are formulated as QUBO models
  - Understand the relationship between QUBO and Ising Hamiltonians
  - Study the principles of variational quantum algorithms, especially QAOA and VQE
  - Apply these methods to selected benchmark problems
  - Develop a code framework for generating instances, building models, running solvers, and analyzing landscapes
  - Prepare for later experimental and numerical evaluation

## 3. Background: QUBO Modeling

- This should be one of the core theory sections
- 3.1 What is QUBO?
  - Define QUBO in words
  - Explain binary variables and quadratic objective form
  - Explain why QUBO is important in combinatorial optimization

- 3.2 Why QUBO is useful
  - QUBO acts as a common modeling language for many problems
  - It is relevant because many constrained problems can be rewritten using penalty terms
  - It provides a bridge between classical optimization and quantum hardware

- 3.3 Penalty-based reformulation idea
  - Explain the basic idea of converting constraints into penalties
  - Keep it conceptual, not too algebra-heavy
  - Mention that this is central to turning classical formulations into unconstrained quadratic binary models

- 3.4 Relevance to this project
  - explain that QUBO is the starting point of the project pipeline
  - mention that benchmark problems will first be encoded into QUBO before further analysis

## 4. Considered Benchmark Problems

- This section should focus only on the problems we are actually using, which are MaxCut and MinVertexCover
- 4.1 Why these benchmark problems were selected
  - widely studied in optimization and quantum algorithm literature
  - graph-based and easy to visualize
  - suitable for testing QUBO encoding and variational methods

- 4.2 MaxCut
  - define the problem clearly
  - explain objective in simple words
  - mention application examples
    - circuit partitioning
    - network design
    - clustering / graph partitioning intuition
  - explain how MaxCut can be expressed in QUBO form

- 4.3 MinVertexCover
  - define the problem clearly
  - explain objective in simple words
  - mention application examples
    - network monitoring
    - resource placement
    - covering constraints on graphs
  - explain how MinVertexCover is expressed in QUBO form
  - emphasize penalty use within the formulation

## 5. From QUBO to Ising Formulations

- we can merge all Ising-related discussion into one focused section here instead of scattering it
- 5.1 What is an Ising formulation?
  - explain spin variables versus binary variables
  - explain couplings and local fields at a conceptual level

- 5.2 Why convert QUBO to Ising?
  - some quantum optimization settings are naturally expressed as Hamiltonians
  - Ising form is directly meaningful in physics language
  - it helps connect classical optimization formulations to quantum algorithms and hardware-oriented models

- 5.3 Basic QUBO-to-Ising mapping idea
  - explain the binary-to-spin substitution idea conceptually
  - do not overdo derivation here
  - mention constant energy shifts and equivalent minima/maxima at a high level

- 5.4 Relevance to this project
  - explain that after constructing QUBO models, the project pipeline includes transforming them into Ising Hamiltonians
  - mention this is important for later algorithmic use and interpretation

## 6. Variational Quantum Algorithms: Conceptual Overview

- one short umbrella section before the algorithm-specific sections to avoids repetition
- Keep this section concise because QAOA and VQE will get their own subsections, stay within project context
  - define VQAs as hybrid quantum-classical methods
  - describe the basic loop
    - parameterized circuit / ansatz
    - measurement of objective
    - classical optimization of parameters
  - explain why VQAs are attractive for near-term devices
    - shorter circuits than fully fault-tolerant methods
    - flexible hybrid structure

- Include pros and cons briefly
  - Pros:
    - near-term relevance
    - flexibility
    - hardware compatibility
  - Cons:
    - optimization difficulty
    - noise sensitivity
    - possible barren plateaus
    - scalability remains open

## 7. Quantum Approximate Optimization Algorithm (QAOA)

- 7.1 What is QAOA?
  - explain QAOA as a variational algorithm for combinatorial optimization
  - mention alternating application of problem and mixer operators

- 7.2 Why QAOA is relevant to this project
  - directly designed for optimization-type objectives
  - naturally connects to MaxCut and other graph problems
  - useful for studying parameter landscapes

- 7.3 Basic workflow of QAOA
  - prepare initial state
  - apply p alternating layers
  - evaluate expectation value
  - optimize parameters
  - sample candidate bitstrings

- 7.4 What has been studied so far from the literature
  - low-depth versus higher-depth behavior
  - importance of parameter optimization
  - relation to quantum annealing
  - note that literature discusses non-adiabatic/diabatic behavior and optimization heuristics

- 7.5 Planned role of QAOA in the project
  - use on QUBO/Ising instances derived from benchmark problems
  - use for basic landscape analysis
  - compare against classical baselines later

## 8. Variational Quantum Eigensolver (VQE)

- 8.1 What is VQE?
  - explain VQE as a hybrid variational method for approximating low-energy states
  - mention expectation estimation plus classical optimization

- 8.2 Why include VQE in this project?
  - VQE gives a second variational perspective
  - useful for studying Hamiltonian-based optimization models
  - useful for landscape and convergence comparisons

- 8.3 Difference between QAOA and VQE in this study
  - QAOA is more structure-driven for optimization
  - VQE is more general variational Hamiltonian minimization
  - both are hybrid, but their ansatz philosophy differs

- 8.4 Planned role of VQE in the project
  - use as a comparative variational method
  - test on selected QUBO/Ising-derived Hamiltonians
  - explore whether landscape behavior differs from QAOA

## 9. Work Completed So Far

- 9.1 Literature review completed
  - studied the QUBO tutorial paper
  - studied Ising formulation paper
  - studied QAOA and VQE source papers
  - studied supporting background on adiabatic / variational quantum computing

- 9.2 Theoretical understanding developed
  - understanding of QUBO modeling principles
  - understanding of penalty terms
  - understanding of QUBO-to-Ising conversion
  - understanding of QAOA and VQE workflows

- 9.3 Practiced QUBO modeling
  - worked on QUBO formulations for MaxCut and MinVertexCover
  - checked whether formulations match intended objective behavior
  - investigated small examples and sanity checks

- 9.4 Code implementation progress
  - planned a code implementation for the research project
  - working on the implementation of the code structure
  - code explained in more detail in next section

## 10. Code Implementation

- This should be a structured, project-oriented section
- 10.1 Overall pipeline
  - Generate or load benchmark problem instance
  - Encode instance into QUBO model
  - Validate formulation on small examples
  - Convert QUBO to Ising form
  - Prepare Hamiltonian/objective for algorithms
  - Run classical baselines
  - Run QAOA
  - Run VQE
  - Decode best solutions
  - Compute metrics
  - Save outputs, histories, plots, and tables

- 10.2 Software components
  - problem instance generator / loader
  - QUBO builder
  - Ising converter
  - classical baseline solver module
  - QAOA runner
  - VQE runner
  - analysis / plotting module
  - experiment configuration management

- 10.3 Validation strategy
  - test on tiny examples
  - compare computed energies with expected values
  - verify decoded solutions satisfy intended problem meaning
  - compare with exact classical solver on small instances

- 10.4 Metrics to be recorded
  - objective value
  - approximation ratio
  - best bitstring found
  - energy value
  - optimization convergence history
  - parameter values
  - runtime
  - success probability or sampling quality if relevant


## 11. Plan for the Remaining Weeks

- 11.1 Next Steps
  - finish implementation modules
  - run end-to-end experiments

- 11.2 Experimental phase
  - generate selected benchmark instances
  - run classical baselines
  - run QAOA and VQE
  - gather histories, objective values, and plots

- 11.3 Analysis phase
  - compare algorithm behavior
  - interpret convergence and landscape observations
  - study strengths and weaknesses on chosen benchmarks


## 12. Conclusion

- Short section
- Summarize the current stage of the research/project
- Re-emphasize that the midterm phase has focused on:
  - conceptual foundations
  - modeling framework
  - benchmark problem selection
  - implementation planning and early development
- End with a forward-looking sentence
  - the remaining half of the project will focus on implementation completion, experimentation, and analysis

## References

- Include the papers from syllabus that we already studied and actually cite in the report

1. Glover, Kochenberger, Du
2. Lucas
3. Farhi, Goldstone, Gutmann
4. Peruzzo et al.
5. Zhou et al.
6. Albash & Lidar

---
