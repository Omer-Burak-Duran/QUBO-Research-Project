# MIDTERM REPORT DRAFT

## Title Page

- Report title
  - Midterm Report: Variational Quantum Algorithms for Combinatorial Optimization and Modeling
- Name, Course, Semester, Instructor

## 1. Introduction

Many important real-world optimization tasks can be formulated as combinatorial optimization problems. In such problems, the goal is to select the best solution from a large set of discrete possibilities. Examples arise in graph partitioning, covering problems, scheduling, routing, and resource allocation. These problems are often difficult to solve exactly, especially as the problem size grows. Their computational difficulty makes them important benchmark cases for both classical and quantum optimization research.

Quantum computing offers a different framework for representing and approaching such problems. In particular, optimization problems can often be reformulated into mathematical forms that are compatible with quantum-inspired and quantum-native methods. One of the most important of these forms is the Quadratic Unconstrained Binary Optimization (QUBO) model, which provides a common representation for many combinatorial problems [1]. In addition, QUBO models are closely related to Ising Hamiltonians, which are natural objects in physics-based quantum optimization settings [2]. This connection makes QUBO modeling especially useful as a bridge between classical optimization problems and quantum computational methods.

The central idea of this independent study is to follow this bridge in a structured way. The study begins by expressing selected classical optimization problems in QUBO form. When appropriate, these formulations are then converted into equivalent Ising representations in order to connect them to Hamiltonian-based quantum methods. On top of this modeling framework, the study examines two important variational quantum algorithms: the Quantum Approximate Optimization Algorithm (QAOA) [3] and the Variational Quantum Eigensolver (VQE) [4]. These algorithms are studied as candidate methods for solving or analyzing optimization problems on near-term quantum devices.

The practical aim of the project is to develop a coherent understanding that extends from mathematical modeling to algorithmic application. This includes learning how constrained classical problems are translated into penalty-based QUBO models, understanding how these models relate to Ising Hamiltonians, and investigating how variational quantum algorithms can be applied to such formulations. A further aim is to connect theoretical study with implementation by building a computational framework that can generate benchmark instances, construct models, run algorithms, and analyze results. In this way, the project is not limited to conceptual study, but also moves toward practical experimentation in the near-term quantum computing setting.

This midterm report presents the current state of the project. Its purpose is fourfold. First, it summarizes the theoretical background studied so far, with emphasis on QUBO modeling, Ising formulations, and variational quantum algorithms. Second, it documents the progress already made in understanding and formulating selected benchmark problems. Third, it explains the implementation direction of the project, including the planned computational pipeline and validation strategy. Fourth, it defines the remaining steps for the rest of the semester, including experimental evaluation and further analysis.

The remainder of this report is organized as follows. Section 2 states the research objectives of the study. Section 3 introduces the background of QUBO modeling. Section 4 presents the benchmark problems considered in the project, namely MaxCut and Minimum Vertex Cover. Section 5 explains the connection between QUBO and Ising formulations. Section 6 gives a brief conceptual overview of variational quantum algorithms, followed by separate sections on QAOA and VQE. Section 9 summarizes the work completed so far. Section 10 describes the current implementation framework and development direction. Section 11 outlines the plan for the remaining weeks of the semester, and Section 12 concludes the report.


## 2. Research Objectives

The main objectives of this independent study are listed below:

1. **To learn how benchmark combinatorial optimization problems can be formulated as QUBO models.**
   A central objective of the project is to understand how discrete optimization problems can be rewritten in the Quadratic Unconstrained Binary Optimization framework. This includes identifying binary decision variables, expressing objective functions in quadratic form, and incorporating constraints through penalty terms [1].

2. **To understand the relationship between QUBO formulations and Ising Hamiltonians.**
   Since many quantum optimization approaches are naturally described in terms of Hamiltonians, it is important to study how binary QUBO models are mapped into spin-based Ising formulations. This objective includes understanding the binary-to-spin variable transformation and the role of couplings, local fields, and constant energy shifts in this mapping [2].

3. **To study the principles of variational quantum algorithms, with emphasis on QAOA and VQE.**
   Another objective is to build a clear conceptual understanding of hybrid quantum-classical optimization methods. In particular, the study focuses on the structure, workflow, and motivation of the Quantum Approximate Optimization Algorithm (QAOA) [3] and the Variational Quantum Eigensolver (VQE) [4], as well as their relevance to near-term quantum computing.

4. **To apply these modeling and algorithmic ideas to selected benchmark problems.**
   The project aims to move beyond general theory by applying QUBO modeling and variational methods to concrete benchmark problems. In the current phase of the study, the main focus is on graph-based problems that are suitable for both formulation and testing, especially MaxCut and Minimum Vertex Cover.

5. **To develop a computational framework for implementation and analysis.**
   A practical objective of the project is to design and implement a code framework that supports the full research pipeline. This includes generating or loading benchmark instances, constructing QUBO and Ising models, running classical and variational solvers, validating small examples, and analyzing optimization behavior through numerical outputs and landscape-related observations.

6. **To prepare for later experimental and numerical evaluation.**
   The final objective of the current midterm phase is to establish a strong foundation for the second half of the project. This includes preparing the theoretical background, modeling approach, and software structure needed for later experiments, performance comparisons, convergence analysis, and result interpretation.

Together, these objectives define the project as a study that combines theoretical understanding, mathematical modeling, algorithmic investigation, and practical implementation within the broader context of near-term quantum optimization.

## 3. Background: QUBO Modeling

### 3.1 What is QUBO?

Quadratic Unconstrained Binary Optimization, abbreviated as QUBO, is a mathematical optimization framework in which the objective is expressed as a quadratic function of binary decision variables [1]. In this setting, each variable can take only one of two values, typically 0 or 1. The task is to choose the binary assignment that minimizes or maximizes the objective function.

The term *quadratic* means that the objective function may contain both linear terms and pairwise product terms between variables. The linear terms represent the individual contribution of each variable, while the quadratic terms represent interactions between pairs of variables. The term *unconstrained* means that the final optimization model is written without explicit constraints. Instead, the effect of constraints is incorporated into the objective function itself, usually through penalty terms.

QUBO is important in combinatorial optimization because many discrete decision problems can be expressed in this form [1]. A wide range of graph problems, assignment problems, partitioning problems, and covering problems can be reformulated as QUBO models. This makes QUBO a useful common representation for studying different optimization tasks within a single mathematical framework.

### 3.2 Why QUBO is useful

One of the main strengths of QUBO is that it acts as a common modeling language for many different optimization problems [1]. Instead of treating each problem type with a completely separate formulation, QUBO provides a unified structure in which a broad class of combinatorial problems can be represented using binary variables and quadratic coefficients. This unifying role is valuable both for theoretical study and for implementation.

QUBO is also useful because many constrained optimization problems can be rewritten in unconstrained form by adding suitable penalty terms to the objective function [1]. This means that constraints such as selection rules, coverage requirements, or logical conditions do not always need to be handled separately. They can instead be absorbed into the optimization objective in a controlled way. As a result, classical constrained formulations can often be translated into a form that is more convenient for certain solvers and more compatible with quantum-oriented models.

A further reason for the importance of QUBO is its close connection to the Ising model, which is widely used in physics and quantum optimization [1][2]. Because of this relationship, QUBO serves as a bridge between classical optimization formulations and Hamiltonian-based quantum representations. This bridge is especially relevant in studies that aim to connect industrial or graph-based optimization problems to near-term quantum algorithms and hardware settings.

### 3.3 Penalty-based reformulation idea

A key idea behind QUBO modeling is penalty-based reformulation. In many classical optimization problems, the objective function is accompanied by constraints that define which solutions are feasible. In the QUBO approach, these constraints are converted into penalty expressions and added to the objective function [1]. The penalty is designed so that feasible solutions receive little or no extra cost, while infeasible solutions receive a larger cost.

Conceptually, this means that the optimization process is guided toward valid solutions not by explicit constraints, but by the structure of the objective function itself. If the penalty terms are chosen appropriately, the optimal solution of the QUBO model will correspond to a valid solution of the original constrained problem. In this way, the constrained problem is transformed into an unconstrained binary optimization problem.

This reformulation idea is central to QUBO modeling. It is the main mechanism that allows classical formulations to be translated into quadratic binary form. For that reason, understanding penalty design is one of the most important conceptual steps in learning how to build QUBO models for practical problems.

### 3.4 Relevance to this project

QUBO modeling forms the starting point of the project pipeline. In this study, selected benchmark optimization problems are first expressed in QUBO form before any further algorithmic step is considered. This makes QUBO the main entry point between the original classical problem statement and the later quantum-oriented formulation.

In practical terms, the benchmark problems considered in this project will first be encoded using binary variables and quadratic objective functions, with constraints incorporated through penalties where necessary. After this step, the resulting QUBO models can be analyzed directly, validated on small instances, and then converted into Ising form when needed for Hamiltonian-based interpretation and variational quantum algorithms.

For this reason, QUBO modeling is not only background theory in this report. It is a core component of the entire research workflow. A clear understanding of QUBO is necessary in order to study benchmark formulations correctly, connect them to Ising Hamiltonians, and prepare them for later use with QAOA and VQE.


## 4. Considered Benchmark Problems

This project focuses on two benchmark combinatorial optimization problems: **MaxCut** and **Minimum Vertex Cover**. Both problems are defined on graphs and are well suited for studying the full modeling-to-algorithm pipeline developed in this work. They provide concrete test cases for QUBO formulation, QUBO-to-Ising conversion, and later application of variational quantum algorithms.

### 4.1 Why these benchmark problems were selected

MaxCut and Minimum Vertex Cover were selected for several reasons. First, both are widely studied in the combinatorial optimization literature and also appear frequently in the quantum optimization literature [1][2][3][5]. This makes them suitable benchmark problems for connecting the present study to established formulations and algorithmic discussions.

Second, both problems are graph-based and therefore relatively easy to visualize and interpret. A graph representation makes it easier to understand the meaning of the variables, constraints, and objective functions. This is especially useful when checking whether a QUBO model matches the intended problem behavior on small examples.

Third, these problems are well suited for testing both modeling ideas and algorithmic methods. MaxCut provides a clean example of an optimization objective that can be expressed naturally in quadratic binary form [1][3]. Minimum Vertex Cover, on the other hand, is especially useful for studying penalty-based reformulation, since the covering constraints play a central role in its QUBO construction [1][2]. Together, these two problems provide a balanced set of benchmark cases for the current phase of the project.

### 4.2 MaxCut

The MaxCut problem is defined on an undirected graph. The goal is to divide the set of vertices into two disjoint groups in such a way that the number of edges crossing between the two groups is as large as possible. In other words, the objective is to place connected vertices on opposite sides of the partition whenever possible.

In simple terms, MaxCut seeks the partition that cuts the maximum number of edges. If two endpoints of an edge are assigned to different groups, that edge contributes to the cut. If they are assigned to the same group, that edge does not contribute. The optimization task is therefore to find the assignment of vertices that maximizes the total number, or total weight, of edges crossing the partition.

MaxCut has practical and conceptual relevance in several application areas. It appears in **circuit partitioning**, where a system may be divided into components while trying to optimize interconnections. It also appears in **network design** and related partitioning tasks. More broadly, it carries a useful **clustering and graph partitioning intuition**, since the problem is concerned with separating a graph into two parts based on edge relationships [1][3].

An important reason for choosing MaxCut in this project is that it can be expressed in QUBO form in a direct and natural way [1]. Binary variables are used to represent the side of the partition to which each vertex belongs. The objective function is then constructed so that an edge contributes positively when its two endpoints are assigned to different groups. This leads to a quadratic binary objective without the need for complex constraint handling. Because of this clean structure, MaxCut serves as a convenient starting benchmark for studying QUBO modeling and variational optimization methods such as QAOA [3][5].

### 4.3 Minimum Vertex Cover

The Minimum Vertex Cover problem is also defined on an undirected graph. A vertex cover is a subset of vertices with the property that every edge in the graph has at least one endpoint contained in the subset. The goal of the problem is to find such a subset with the smallest possible number of vertices.

In simple terms, the objective is to choose as few vertices as possible while still covering all edges. Every edge must be “touched” by at least one selected vertex. This creates a natural tradeoff between minimizing the number of selected vertices and satisfying the coverage requirement for the full graph.

Minimum Vertex Cover has several practical interpretations. It is relevant in **network monitoring**, where selected nodes may be used to observe or control all connections in a network. It can also be viewed as a **resource placement** problem, where limited resources must be positioned so that every interaction or link is covered. More generally, it is a standard example of a graph problem built around **covering constraints** [1][2].

In QUBO form, Minimum Vertex Cover is more instructive than MaxCut because the formulation depends explicitly on penalty terms [1]. Binary variables indicate whether each vertex is selected for the cover. The objective includes a term that encourages selecting as few vertices as possible. However, the edge-covering requirements must also be enforced. This is achieved by adding penalty expressions that increase the objective value whenever an edge is left uncovered. In this way, infeasible solutions become less favorable than feasible ones.

For this reason, Minimum Vertex Cover is an especially useful benchmark for this project. It illustrates the central QUBO idea that classical constraints can be absorbed into the objective function through penalties. Studying this problem helps clarify how constrained graph problems are translated into unconstrained quadratic binary models, which is one of the main themes of the report.


## 5. From QUBO to Ising Formulations

After expressing a combinatorial optimization problem in QUBO form, a natural next step is to relate this formulation to the Ising model. This connection is important because QUBO belongs primarily to the language of binary optimization, while the Ising model belongs to the language of spin systems and Hamiltonians in physics [1][2]. Since this project aims to connect classical optimization problems to quantum algorithms, it is useful to treat the QUBO-to-Ising relationship in a dedicated section rather than discussing it in scattered form.

### 5.1 What is an Ising formulation?

An Ising formulation represents an optimization problem in terms of spin variables rather than binary variables. In a QUBO model, variables usually take values in {0,1}. In an Ising model, the corresponding spin variables usually take values in {-1,+1}. Although these two representations use different variable sets, they can encode equivalent optimization problems.

Conceptually, an Ising model is defined by an energy function that depends on individual spins and pairwise interactions between spins [2]. The individual-spin terms are often called **local fields**, and they describe the tendency of a single spin to favor one state over the other. The pairwise interaction terms are often called **couplings**, and they describe how pairs of spins influence each other. A positive or negative coupling can make two spins prefer to align or anti-align, depending on the convention used.

From an optimization point of view, the Ising formulation assigns an energy value to each spin configuration, and the goal is to find the configuration with the lowest energy. In this sense, the Ising model serves as a Hamiltonian-based optimization representation, where the optimal solution is encoded in a ground-state configuration.

### 5.2 Why convert QUBO to Ising?

There are several reasons why converting QUBO to Ising form is useful. First, many quantum optimization settings are naturally described in terms of Hamiltonians rather than classical objective functions [2][6]. Since the Ising model is already written as an energy function over spins, it fits directly into this framework.

Second, the Ising formulation is meaningful in the language of physics. Terms such as spins, couplings, local fields, energy landscape, and ground state arise naturally in quantum mechanics and condensed matter contexts. Expressing an optimization problem in Ising form therefore makes it easier to interpret the problem in a way that is compatible with Hamiltonian-based algorithms and physical implementations.

Third, the conversion helps connect classical optimization formulations to quantum algorithms and hardware-oriented models. A QUBO model may begin as a classical reformulation of a graph or covering problem, but once it is written in Ising form, it can be viewed as an optimization Hamiltonian. This makes it easier to discuss how the problem may be handled by methods such as QAOA, VQE, and related quantum optimization approaches [2][3][4][6].

### 5.3 Basic QUBO-to-Ising mapping idea

The mapping from QUBO to Ising is based on a simple change of variables. A binary variable in {0,1} can be rewritten in terms of a spin variable in {-1,+1} through a linear substitution. Conceptually, this means that each binary decision variable is replaced by an equivalent spin representation. After this substitution is applied to all variables in the QUBO objective, the result can be rearranged into Ising form.

At a high level, the linear terms of the QUBO model become local-field terms in the Ising Hamiltonian, while the quadratic terms become spin-spin coupling terms. In this way, the structure of the optimization problem is preserved, but it is rewritten in a form that uses spin variables instead of binary variables.

During this conversion, a constant term usually appears in the energy expression. This constant shift does not change which configuration is optimal, because it affects all candidate solutions equally. For that reason, the QUBO and Ising formulations are considered equivalent from the optimization perspective even if their objective values are not numerically identical term by term. What matters is that the mapping preserves the location of the optimal solution, or more generally the ordering of relevant configurations at the level needed for optimization and interpretation.

### 5.4 Relevance to this project

In this project, the QUBO-to-Ising transformation is an important step in the overall research pipeline. The benchmark problems are first formulated as QUBO models, since QUBO provides a convenient and general optimization language for expressing the original combinatorial problems. After this stage, the formulations are transformed into Ising Hamiltonians when a Hamiltonian-based representation is needed.

This transformation is important for two reasons. First, it gives a physics-oriented interpretation of the optimization problem, which is helpful when discussing energy landscapes, Hamiltonians, and ground states. Second, it prepares the problem for later algorithmic use, since variational quantum methods such as QAOA and VQE are naturally described in terms of operators and Hamiltonian expectations [3][4][5].

For this reason, the QUBO-to-Ising step is not only a mathematical reformulation. It is the point where the project moves from classical binary optimization language toward the Hamiltonian language needed for quantum algorithm analysis and implementation.


## 6. Variational Quantum Algorithms: Conceptual Overview

Variational Quantum Algorithms (VQAs) are hybrid quantum-classical methods designed to use both a quantum processor and a classical optimizer in the same computational loop [3][4]. They are especially important in the near-term quantum computing setting, where quantum devices are limited by noise, decoherence, and circuit depth. Rather than relying on long, fully fault-tolerant computations, VQAs aim to solve optimization or eigenvalue problems through repeated short quantum executions combined with classical parameter updates.

The basic idea of a VQA is as follows. A parameterized quantum circuit, often called an **ansatz**, is prepared on a quantum device. The circuit depends on a set of adjustable parameters. After the circuit is executed, measurements are performed in order to estimate an objective quantity, such as an energy expectation value or an optimization cost. These measurement results are then sent to a classical optimizer, which updates the parameters in an attempt to improve the objective. This hybrid loop is repeated until a satisfactory result is obtained [3][4].

VQAs are attractive for near-term devices for several reasons. First, they typically use shorter and more practical circuits than algorithms designed for fully error-corrected quantum computers. Second, their hybrid structure allows part of the computational burden to be handled classically, while the quantum device is used only for state preparation and measurement. This makes them a natural candidate class of methods for current and near-future hardware [4][5].

Within the context of this project, VQAs are relevant because they provide a practical algorithmic layer on top of the QUBO and Ising formulations developed earlier in the report. Once an optimization problem has been expressed as a Hamiltonian or cost operator, a variational method can be used to search for low-energy or high-quality solutions through parameter optimization. In this sense, VQAs provide a usable computational framework for studying combinatorial optimization problems on near-term quantum devices.

At the same time, VQAs have important limitations. Their performance depends strongly on the quality of the parameter optimization, and the optimization landscape can be difficult to navigate in practice [5]. They are also sensitive to hardware noise and sampling errors, since the objective function is estimated through repeated measurements. In addition, some variational settings may suffer from flat optimization landscapes, often discussed under the name of barren plateaus, which can make training difficult. More generally, the large-scale performance and scalability of VQAs remain open research questions.

Because of these features, VQAs are best viewed as promising but still actively studied methods. They are attractive because of their near-term relevance, flexibility, and compatibility with current hardware, but they also raise important questions about optimization behavior, robustness, and scaling. In the following sections, the two specific VQAs considered in this project, QAOA and VQE, are discussed separately.


## 7. Quantum Approximate Optimization Algorithm (QAOA)

### 7.1 What is QAOA?

The Quantum Approximate Optimization Algorithm (QAOA) is a variational quantum algorithm developed for combinatorial optimization problems [3]. It is designed to produce candidate solutions to discrete optimization tasks by preparing a parameterized quantum state and adjusting the parameters so that the state is biased toward good solutions.

A defining feature of QAOA is its layered structure. The algorithm alternates between two types of operators: a **problem operator**, which encodes the optimization objective, and a **mixer operator**, which drives transitions between computational basis states [3]. The problem operator is constructed from the cost function or Hamiltonian associated with the optimization problem, while the mixer operator is chosen to explore the search space. By repeating these alternating applications over several layers, QAOA generates a family of states controlled by variational parameters.

In this way, QAOA combines ideas from Hamiltonian optimization, quantum circuit design, and classical parameter tuning. The quality of the final result depends on both the chosen circuit depth and the success of the classical optimization over the variational parameters.

### 7.2 Why QAOA is relevant to this project

QAOA is highly relevant to this project because it is directly designed for optimization-type objectives [3]. Unlike more general-purpose quantum methods, QAOA is built around a cost Hamiltonian that represents the problem of interest. This makes it a natural candidate for studying combinatorial optimization problems after they have been formulated in QUBO and Ising form.

It also connects naturally to graph-based benchmark problems such as MaxCut. In fact, MaxCut is one of the best-known example problems in the original QAOA literature [3]. Since the present project focuses on graph-based problems and Hamiltonian-based formulations, QAOA provides a direct algorithmic path from model construction to variational solution search.

A further reason for its relevance is that QAOA is useful for studying parameter landscapes and variational behavior [5]. Because the algorithm depends on a set of tunable angles, it provides a concrete setting in which one can examine optimization difficulty, parameter sensitivity, and convergence behavior. This makes it suitable not only as a solver candidate, but also as an object of landscape analysis within the broader goals of the project.

### 7.3 Basic workflow of QAOA

The basic workflow of QAOA begins with the preparation of a simple initial quantum state, usually a uniform superposition over computational basis states [3]. This initial state provides a neutral starting point from which the algorithm can explore different candidate solutions.

Next, the algorithm applies a sequence of alternating layers. Each layer consists of one application of the problem unitary and one application of the mixer unitary, controlled by variational parameters. If the circuit contains (p) such alternating layers, then the algorithm is referred to as a depth-(p) or level-(p) QAOA circuit [3].

After the parameterized state is prepared, measurements are used to estimate the expectation value of the cost Hamiltonian. This expectation value serves as the objective for the classical optimization loop. A classical optimizer then updates the parameters in order to improve the measured objective value. This process is repeated until the parameter values stabilize or another stopping condition is reached.

Once a good parameter set has been found, the optimized circuit can be sampled multiple times in the computational basis. These samples produce candidate bitstrings, which can then be decoded back into solutions of the original optimization problem. In this way, QAOA combines expectation-based parameter training with solution extraction through measurement sampling.

### 7.4 What has been studied so far from the literature

The literature studied so far shows that QAOA is conceptually simple but practically rich. The original QAOA paper introduced the algorithm as a general framework for approximate combinatorial optimization and analyzed its behavior on benchmark cases such as MaxCut [3]. One key idea from this line of work is that increasing the depth parameter (p) improves the expressive power of the circuit, although at the cost of more parameters and more difficult optimization.

A recurring theme in the literature is the difference between low-depth and higher-depth behavior. At low depth, QAOA can already produce nontrivial approximation performance and can sometimes be analyzed theoretically [3]. At higher depth, performance may improve, but the classical optimization becomes more challenging because the parameter space becomes larger and the landscape more complex [5]. This makes parameter selection and optimization strategy a central practical issue.

Another important topic is the relationship between QAOA and quantum annealing. Since QAOA can be viewed as alternating controlled evolutions under the problem and mixer Hamiltonians, it has an intuitive connection to discretized annealing-like processes [3][5]. However, later studies also show that QAOA is not limited to purely adiabatic behavior. In particular, the literature discusses the possibility that optimized QAOA protocols can exploit non-adiabatic or diabatic mechanisms, rather than simply approximating slow annealing [5]. This makes the algorithm interesting not only as an optimization method, but also as a tool for studying different solution-generation mechanisms.

The literature also emphasizes the importance of good parameter optimization heuristics [5]. Because naive optimization can become difficult as circuit depth grows, practical studies often focus on initialization strategies, parameter patterns, and other techniques that make the outer classical loop more effective. This aspect is especially relevant to the present project, where implementation and landscape-related behavior are part of the research focus.

### 7.5 Planned role of QAOA in the project

In this project, QAOA is planned to serve as one of the main variational algorithms applied to the benchmark problems after QUBO construction and Ising conversion. The algorithm will be tested on the Hamiltonian instances derived from the selected graph problems, with particular focus on the current benchmark set of MaxCut and Minimum Vertex Cover.

Beyond its role as a candidate solver, QAOA will also be used for basic landscape analysis. Since the algorithm is parameterized by alternating angles, it provides a convenient framework for examining how the objective value changes across parameter space, how optimization behaves at different depths, and whether certain structures or difficulties appear in the landscape.

Later in the project, QAOA results are expected to be compared with classical baselines and with the second variational method considered in this study, namely VQE. In this way, QAOA will contribute both to the practical computational part of the project and to the broader analysis of variational behavior on combinatorial optimization problems.


## 8. Variational Quantum Eigensolver (VQE)

### 8.1 What is VQE?

The Variational Quantum Eigensolver (VQE) is a hybrid quantum-classical algorithm designed to approximate low-energy states of a Hamiltonian [4]. In its standard form, the goal is to prepare a parameterized quantum state whose energy expectation value is as low as possible. Because the ground state of a Hamiltonian corresponds to its minimum energy state, minimizing this expectation value provides a way to approximate the ground state and its energy.

Like other variational methods, VQE combines quantum state preparation with classical optimization. A parameterized quantum circuit is first chosen as an ansatz. This circuit prepares a trial quantum state depending on a set of adjustable parameters. The quantum device is then used to estimate the expectation value of the target Hamiltonian with respect to this state. These estimated expectation values are passed to a classical optimizer, which updates the circuit parameters in order to reduce the measured energy [4]. The process is repeated until the energy converges or another stopping condition is reached.

VQE was originally introduced in the context of quantum chemistry and eigenvalue problems [4], but its broader variational structure makes it relevant to any setting where a problem can be encoded as a Hamiltonian and the objective is related to finding low-energy configurations. For that reason, VQE can also be considered in optimization studies once a combinatorial problem has been mapped into Hamiltonian form.

### 8.2 Why include VQE in this project?

VQE is included in this project because it provides a second variational perspective in addition to QAOA. While both methods are hybrid and Hamiltonian-based, they approach the optimization task with different circuit philosophies and different levels of problem-specific structure. Including VQE therefore makes the study more balanced and allows the project to compare two important classes of near-term variational methods.

VQE is also useful because the benchmark problems in this project are eventually expressed as Ising Hamiltonians. Once a problem has been written in Hamiltonian form, VQE can be applied directly as a variational minimization method. This makes it relevant not only for general quantum algorithm study, but also for the specific modeling pipeline developed in this report.

Another reason for including VQE is that it creates an opportunity for comparing landscape and convergence behavior across two different variational approaches. Since the project is interested not only in obtaining solutions but also in understanding algorithmic behavior, VQE offers a useful contrast to QAOA. It may reveal differences in optimization difficulty, parameter sensitivity, and solution quality even when both methods are applied to the same Hamiltonian instance.

### 8.3 Difference between QAOA and VQE in this study

Although QAOA and VQE are both hybrid variational algorithms, they are conceptually different in important ways. In this study, QAOA is treated as a more structure-driven algorithm for combinatorial optimization. Its ansatz is built from alternating applications of a problem Hamiltonian and a mixer Hamiltonian, so the circuit design is directly tied to the optimization problem itself [3]. This makes QAOA especially natural for graph-based cost functions and discrete optimization settings.

VQE, by contrast, is treated here as a more general variational Hamiltonian minimization method [4]. Its basic objective is not specifically tied to combinatorial optimization, but rather to finding low-energy states of a given Hamiltonian. As a result, the choice of ansatz in VQE is typically more flexible and less tightly determined by the original optimization structure. This makes VQE broader in principle, but also means that its success depends strongly on ansatz design and parameter optimization.

Thus, the main difference in this study is that QAOA is more problem-structured, while VQE is more general-purpose. Both algorithms rely on the same hybrid loop of state preparation, measurement, and classical optimization, but their ansatz philosophies differ. This difference is one of the reasons why comparing them is meaningful within the context of the project.

### 8.4 Planned role of VQE in the project

In this project, VQE is planned to serve as a comparative variational method alongside QAOA. After benchmark problems are formulated in QUBO form and converted into Ising Hamiltonians, selected instances will be used as inputs for VQE-based experiments. This will allow the study to test how a more general variational eigensolver behaves on optimization-derived Hamiltonians.

The role of VQE is therefore not only to provide another candidate solution method, but also to support comparison. By applying both QAOA and VQE to related benchmark instances, the project can examine whether the two methods behave differently in terms of convergence, parameter sensitivity, and overall variational performance.

A further planned use of VQE is in basic landscape-related analysis. Since VQE and QAOA use different ansatz structures, their optimization landscapes may also differ. Exploring whether these differences appear in practice is part of the motivation for including VQE in the project. In this sense, VQE contributes both as a solver candidate and as a tool for comparative algorithmic study.


## 9. Work Completed So Far

### 9.1 Literature review completed

A substantial part of the work completed so far has consisted of a focused literature review on the main theoretical components of the project. The first major source studied was the QUBO modeling tutorial by Glover, Kochenberger, and Du, which provided the main conceptual foundation for understanding how combinatorial optimization problems can be expressed in quadratic unconstrained binary form [1]. This was followed by a study of the Ising formulation paper by Lucas, which clarified how a broad range of discrete optimization problems can be represented in spin-based Hamiltonian language [2].

In parallel with the modeling literature, the core source papers on the two selected variational algorithms were studied. The original QAOA paper by Farhi, Goldstone, and Gutmann was examined to understand the algorithmic structure, its optimization-oriented design, and its application to benchmark problems such as MaxCut [3]. The VQE paper by Peruzzo et al. was studied in order to understand the general hybrid variational framework, including expectation estimation and classical parameter optimization [4]. In addition, the QAOA performance study by Zhou et al. was reviewed to gain insight into higher-depth behavior, parameter optimization strategies, and the relation between QAOA and annealing-type dynamics [5].

Supporting background was also studied in order to place these methods in a broader context. In particular, background reading on adiabatic and variational quantum computing was carried out using the review by Albash and Lidar [6]. This helped strengthen the conceptual connection between optimization Hamiltonians, adiabatic reasoning, and near-term variational methods.

### 9.2 Theoretical understanding developed

As a result of the literature review, a stronger theoretical understanding of the project topic has been developed. First, the general principles of QUBO modeling have been studied in detail. This includes the use of binary decision variables, the construction of quadratic objective functions, and the idea of treating QUBO as a unifying modeling language for a wide class of combinatorial optimization problems [1].

Second, an improved understanding of penalty-based reformulation has been developed. This includes the role of penalty terms in absorbing classical constraints into the objective function and the conditions under which such penalties preserve the intended meaning of the original optimization problem [1]. Since penalty design is central to QUBO modeling, this has become one of the most important theoretical components studied so far.

Third, the relationship between QUBO formulations and Ising Hamiltonians has been studied at a conceptual level. This includes the binary-to-spin variable transformation, the interpretation of couplings and local fields, and the reason why QUBO and Ising forms are closely connected in quantum optimization settings [2]. This understanding is important because it links classical discrete modeling to Hamiltonian-based quantum algorithms.

Finally, the main workflows of QAOA and VQE have been studied and compared. This includes the shared hybrid quantum-classical loop, the role of parameterized circuits, the measurement of objective functions, and the classical optimization of circuit parameters [3][4]. The study has also clarified the main difference between the two methods: QAOA is more directly structured around optimization Hamiltonians, while VQE is a more general variational energy minimization framework.

### 9.3 Practiced QUBO modeling

Beyond theoretical reading, practical work has also been carried out on QUBO modeling itself. In particular, QUBO formulations for the selected benchmark problems, MaxCut and Minimum Vertex Cover, have been studied and worked through in detail. This step was important for moving from general background knowledge to concrete problem encoding.

During this process, attention was given not only to writing down formulations, but also to checking whether they matched the intended objective behavior of the original problems. For MaxCut, this meant examining whether the quadratic objective correctly rewarded assignments that place connected vertices on opposite sides of the cut. For Minimum Vertex Cover, this meant examining whether the formulation correctly balanced vertex minimization with coverage enforcement through penalties.

Small examples and sanity checks were also investigated in order to verify the meaning of the formulations. This helped confirm whether feasible and infeasible assignments behaved as expected, whether objective values reflected the intended optimization goals, and whether the penalty terms were functioning in the correct way. These checks were useful for building confidence before moving toward larger-scale implementation.

### 9.4 Code implementation progress

In addition to the theoretical and formulation-oriented work, progress has also been made on the implementation side of the project. A code framework for the overall research pipeline has been planned, with the goal of supporting problem generation, QUBO construction, Ising conversion, algorithm execution, and result analysis within a single structured workflow.

At the current stage, the implementation effort is focused on building the code structure needed for later experiments. This includes organizing the main modules, defining the intended pipeline, and preparing the components that will later be used for validation, solver execution, and numerical analysis. The implementation is therefore in an active development phase rather than a completed experimental phase.

The code-related part of the project will be explained in more detail in the next section, where the planned pipeline, software components, validation strategy, and target metrics are described more systematically.


## 10. Code Implementation

This section describes the implementation direction of the project from a software and workflow perspective. At the current midterm stage, the purpose of the codebase is to support the full research pipeline in a modular and testable way. The implementation is designed not only to run variational quantum algorithms, but also to connect problem generation, model construction, validation, baseline comparison, and result analysis within a single framework.

### 10.1 Overall pipeline

The planned implementation follows a structured pipeline. The first step is to generate or load a benchmark problem instance. In the current scope of the project, this primarily refers to graph-based instances for MaxCut and Minimum Vertex Cover. The instance serves as the original classical input from which all later representations are derived.

The second step is to encode the instance into QUBO form. This stage constructs the binary quadratic objective corresponding to the selected problem. For MaxCut, this means building the objective that rewards cut edges. For Minimum Vertex Cover, this means combining the vertex-selection objective with penalty terms that enforce edge coverage.

After the QUBO model is constructed, the formulation is validated on small examples. This stage is important because it checks whether the encoded objective behaves as intended before more advanced algorithms are applied. Small-instance validation helps reveal sign errors, incorrect penalty choices, or decoding mistakes early in the process.

The next step is to convert the QUBO model into Ising form. This produces the Hamiltonian-based representation needed for later quantum-oriented interpretation and algorithm execution. Once the Ising form is obtained, the corresponding Hamiltonian or objective operator is prepared in a form suitable for the selected solvers.

After model preparation, the implementation runs classical baseline methods. These baselines are necessary for checking correctness on small instances and for providing reference values during later comparisons. Following the classical stage, the pipeline runs QAOA and VQE on the same problem instances.

Once algorithm outputs are obtained, the best measured or optimized bitstrings are decoded back into problem-level solutions. These decoded solutions are then checked against the original combinatorial meaning of the benchmark problem. Finally, the pipeline computes relevant performance metrics and stores the outputs in organized form, including numerical results, optimization histories, plots, and tables. This overall design is intended to support both experimentation and later report writing.

### 10.2 Software components

To support the pipeline described above, the codebase is organized into several logical components. The first component is a **problem instance generator or loader**. This module is responsible for either generating benchmark instances programmatically or loading them from predefined sources. It provides the starting data structures for the rest of the workflow.

The second component is the **QUBO builder**. Its role is to translate each benchmark problem instance into a QUBO model. This includes defining binary variables, constructing linear and quadratic terms, and incorporating penalty expressions when the problem requires constraint handling.

The third component is the **Ising converter**. This module takes a QUBO model as input and applies the binary-to-spin mapping to produce the corresponding Ising representation. Its output should include the terms needed to interpret the model as a Hamiltonian, such as local fields, pairwise couplings, and any relevant constant offset.

The fourth component is the **classical baseline solver module**. This part of the code is used to solve small or moderate instances with classical methods in order to provide reference solutions. These results are important both for validation and for later comparison with the variational quantum methods.

The fifth and sixth components are the **QAOA runner** and the **VQE runner**. These modules are responsible for preparing the parameterized ansatz, executing the optimization loop, collecting measurement-based objective values, and returning the best parameter sets and candidate solutions found by each algorithm.

The seventh component is the **analysis and plotting module**. This module collects outputs from all solvers and converts them into interpretable results. Its tasks include computing summary statistics, producing convergence plots, generating tables of results, and supporting landscape-related visualizations where appropriate.

The final component is **experiment configuration management**. This part of the implementation defines how runs are controlled and reproduced. It includes settings such as benchmark type, instance size, penalty coefficients, circuit depth, optimizer selection, number of repetitions, and output paths. A clear configuration structure is important for keeping experiments organized and reproducible.

### 10.3 Validation strategy

A reliable validation strategy is necessary because the implementation combines several nontrivial steps, from problem encoding to algorithm execution. The first level of validation is to test the code on very small examples. On these instances, all configurations can be checked directly or compared against simple expected behavior. This makes it easier to confirm that the QUBO model and its decoding are correct.

A second validation step is to compare computed energies with expected values for selected assignments. This is especially useful when checking QUBO and Ising construction. If a known bitstring should represent a good or bad solution, the corresponding objective or energy value should reflect that expectation. Such checks help verify whether the mapping between mathematical formulation and code implementation is correct.

A third step is to verify that decoded solutions satisfy the intended meaning of the original problem. For example, a decoded MaxCut solution should correspond to a valid partition of the graph, and a decoded Minimum Vertex Cover solution should indeed cover all edges when it is meant to be feasible. This step checks the correctness of the interpretation layer, not only the optimization layer.

A fourth and especially important validation step is to compare results with an exact classical solver on small instances. If the classical exact solution is known, then the best energy, best objective value, and decoded combinatorial solution produced by the implementation can be tested directly against it. This provides a strong reference point before moving to larger instances or variational runs.

### 10.4 Metrics to be recorded

The implementation is designed to record several metrics during experiments. One basic metric is the **objective value** of the decoded solution, expressed in the natural language of the original optimization problem. For example, this may correspond to cut size in MaxCut or cover size in Minimum Vertex Cover.

Another key metric is the **approximation ratio**, especially when comparing variational methods with exact or best-known classical results. This ratio helps evaluate how close the algorithmic output is to the best available solution and is therefore useful in comparative experiments.

The **best bitstring found** is also recorded, since it is the direct discrete output from the variational or classical solver before full interpretation. Closely related to this is the **energy value**, which is especially relevant when working in Ising or Hamiltonian form. Recording both objective value and energy is useful because the problem may be interpreted at more than one representation level.

In addition, the implementation records **optimization convergence history**, such as the sequence of objective or energy values observed during the parameter optimization process. This is important for understanding training behavior and for later discussion of convergence quality. The associated **parameter values** are also recorded, since they are necessary for reproducing runs and analyzing landscape structure.

Finally, the implementation records **runtime** information, since computational cost is an important part of practical evaluation. When relevant, it will also record **success probability**, sampling-based frequencies, or other indicators of **sampling quality**. These are particularly useful in variational settings where the final solution is extracted from repeated circuit measurements rather than from a single deterministic output.

Overall, this implementation framework is intended to support the project not only as a coding exercise, but as a research tool. It is structured to enable systematic experiments, meaningful comparisons, and clear interpretation of results in the later stages of the study.



## 11. Plan for the Remaining Weeks

### 11.1 Next Steps

The next stage of the project will focus on completing the implementation and moving from preparation to systematic experimentation. The immediate priority is to finish the remaining software modules required for the full workflow. This includes finalizing the QUBO construction pipeline, completing the QUBO-to-Ising conversion process, and ensuring that the classical and variational solver interfaces work consistently within the same framework.

After the main modules are completed, the next step will be to run end-to-end experiments on selected benchmark instances. At that stage, the purpose will no longer be only to test individual components, but to confirm that the entire pipeline works correctly from problem generation to final analysis output. This will mark the transition from implementation-focused progress to experiment-focused progress.

### 11.2 Experimental phase

The experimental phase of the project will begin by generating or selecting benchmark instances for the problems studied in this report, namely MaxCut and Minimum Vertex Cover. These instances will be chosen in a way that allows both correctness checks on small examples and broader numerical testing on larger cases.

For each selected instance, classical baseline methods will first be applied. This step will provide reference objective values and exact or near-exact solutions where possible. These results will serve as comparison points for evaluating the variational methods in the next stages.

After the baseline stage, QAOA and VQE will be run on the corresponding QUBO- and Ising-derived Hamiltonians. The experimental goal will be to collect meaningful outputs from both algorithms under controlled settings. This includes not only the final solution quality, but also the internal optimization history and parameter behavior during the variational process.

During this phase, the project will gather numerical results in a structured form. These outputs will include objective values, energy values, parameter histories, convergence traces, and plots that summarize algorithmic behavior. The purpose of this collection step is to create a clear basis for the analysis and interpretation stage that follows.

### 11.3 Analysis phase

Once the experiments have been completed, the final stage of the project will focus on analysis. A central goal of this phase will be to compare the behavior of the algorithms on the selected benchmark problems. This includes examining how QAOA and VQE perform relative to each other and relative to the classical baselines.

Another important goal will be to interpret convergence behavior and landscape-related observations. Since the project is interested not only in final performance but also in variational optimization behavior, the analysis will examine whether the algorithms show different convergence patterns, parameter sensitivities, or optimization difficulties across benchmark instances.

Finally, the analysis phase will study the strengths and weaknesses of the selected methods on the chosen benchmark problems. This includes identifying cases where a formulation or algorithm works well, as well as cases where difficulties appear. These observations will help shape the final conclusions of the project and will provide the basis for the final report at the end of the semester.



## 12. Conclusion

At the current midterm stage, this project has established the main conceptual and practical foundations required for the rest of the study. The work completed so far has focused on understanding how combinatorial optimization problems can be formulated in QUBO form, how these formulations relate to Ising Hamiltonians, and how variational quantum algorithms such as QAOA and VQE can be studied in this context.

The midterm phase has therefore concentrated primarily on four areas. The first has been the development of the necessary conceptual foundations through literature review and theoretical study. The second has been the construction of the modeling framework, especially the role of QUBO reformulation and QUBO-to-Ising conversion. The third has been the selection and study of suitable benchmark problems, with the present report focusing on MaxCut and Minimum Vertex Cover. The fourth has been the planning and early development of the implementation pipeline that will support later experiments.

In this sense, the project has moved beyond a purely exploratory stage and has reached a structured preparation stage. The theoretical background has been studied, the benchmark scope has been defined, and the implementation direction has been organized in a way that supports systematic continuation.

The remaining half of the project will focus on completing the implementation, running experiments on the selected benchmark problems, and analyzing the behavior of the chosen variational methods in comparison with classical baselines.


## References

1. F. Glover, G. Kochenberger, and Y. Du. Quantum Bridge Analytics I: A Tutorial on Formulating and Using QUBO Models. 4OR, 17(4):335–371, 2019.
2. A. Lucas. Ising formulations of many NP problems. Frontiers in Physics, 2:5, 2014.
3. E. Farhi, J. Goldstone, and S. Gutmann. A quantum approximate optimization algorithm.
arXiv preprint arXiv:1411.4028, 2014.
4. A. Peruzzo, J. McClean, P. Shadbolt, et al. A variational eigenvalue solver on a photonic
quantum processor. Nature Communications, 5:4213, 2014.
5. L. Zhou, et al. Quantum Approximate Optimization Algorithm: Performance, Mechanism, and
Implementation on Near-Term Devices. Physical Review X, 10:021067, 2020.
6. T. Albash and D. A. Lidar. Adiabatic quantum computation. Reviews of Modern Physics,
90:015002, 2018.

---
