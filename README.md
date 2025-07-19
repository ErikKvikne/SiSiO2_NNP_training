# Si/SiO₂ Neural Network Potential Training Workflow

This repository contains the workflow developed and used in the master's thesis for modeling oxygen diffusion in silicon/silicon dioxide (Si/SiO₂) interfaces. The project centers on building accurate Neural Network Potentials (NNPs) by combining structure generation, Molecular Dynamics (MD) simulations, Density Functional Theory (DFT) calculations, and model training.

---

## Project Scope

The central aim of this project is to assess how accurately a neural network potential (NNP) trained on DFT data can model the structural and dynamical behavior of Si/SiO₂ interfaces. To this end, the workflow and tools in this repository were developed to support the following objectives:

- Generate a structurally diverse dataset of Si/SiO₂ interfaces using molecular dynamics (MD) and DFT calculations.
- Train a neural network potential on this dataset and evaluate its accuracy in predicting energies and atomic forces.
- Refine the model using active learning, focusing on configurations that challenge the model, including oxygen diffusion events and structural transitions.
- Validate the refined model by comparing structural properties, diffusion behavior, and energies to DFT calculations and existing literature.

---

## Repository Structure

```text
data/                         # Structures and datasets used throughout the project
├── deepmd_dataset/           # Training/validation data for DeepMD models
│   ├── preliminary_dataset/
│   ├── model_devi_additions/
│   └── oxygen_jumps/
└── structures/               # Reference structures and trajectory snapshots
    ├── asio2/
    ├── interfaces/
    ├── oxygen_diffusion_initial/
    └── oxygen_diffusion_refined_model/

dft/                         # DFT automation tools
├── automate_cp2k.py         # Extracts snapshots and generates CP2K inputs
└── copy_dft.sh              # Utility for syncing results from HPC

md_setup/                              # MD job setup utilities
├── frozen_si_interface_example.ipynb  # Example of interface melting/quenching
└── md_job_setup.py                    # Automates LAMMPS job creation from .cif/.data

models/                       # Trained DeepMD models
├── preliminary_dataset_model/
│   ├── 25-03-11_long_run_model.pb
│   └── original_set_seed/    # Models trained with different random seeds
└── oxygen_diffusion_model/
    ├── 25-05-13_model_oxygen_diffusion_main.pb
    └── random_seed/          # Refined models for model deviation studies

structure_generation/               # Interface construction tools
├── bulk_structure_generator.py     # Build crystalline and amorphous bulk structures
├── si_sio2_generator.py            # Generate structured Si/SiO₂ interfaces
├── zsl_example_usage.ipynb         # Full ZSL interface generation pipeline
└── zsl_generator/                  # ZSL-based matching for coherent interfaces
    ├── interface_from_zsl.py
    ├── zsl_analyzer.py
    └── zsl_match.py

templates/                    # Input templates for DFT/MD automation
├── dft/
└── md/

prep.ipynb                    # High-level overview and structure inspection notebook
README.md
```

---

## Key Features

- **Structure Generation**  
  Si/SiO₂ interfaces are generated using both manual matching and ZSL-based lattice matching, ensuring consistency with both crystalline and amorphous structures.

- **DeepMD Simulations**  
  Interface systems are simulated with DeepMD-trained models using MD protocols and selective freezing.

- **DFT Reference Data**  
  CP2K is used to generate forces and energies on snapshots from MD for model training and validation.

- **Model Improvement**  
  Model deviation and targeted oxygen jump simulations enrich the training set, leading to a more robust and transferable model.

---

## Notes


- This repository supports reproducibility and serves as supplementary material for the thesis submitted July 2025.
- The final trained models and reference structures are included for future NNP refinement or analysis.
- This repository includes the core components related to structure generation, simulation setup, and automation used in the thesis. More specific applications, such as density of states (DOS) analysis, detailed postprocessing, and most MD simulation outputs, are not included.