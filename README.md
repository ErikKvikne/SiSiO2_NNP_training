# **Si/SiO₂ Neural Network Potential Training Workflow**

This repository contains the complete workflow used in the master's thesis for simulating and analyzing oxygen diffusion in Si/SiO₂ interfaces. The goal is to generate high-quality datasets using Molecular Dynamics (MD) and Density Functional Theory (DFT) to train Neural Network Potentials (NNPs) that enable large-scale, accurate simulations of semiconductor interfaces.

## **Overview**

The project focuses on:
- Generating crystalline and amorphous Si/SiO₂ interface structures
- Running MD simulations using DeepMD-trained models
- Performing DFT calculations with CP2K for validation and dataset generation
- Training and analyzing NNPs with a focus on oxygen diffusion mechanisms

## Repository Structure

```
data/                         # Contains structures and datasets
├── deepmd_dataset/          # DeepMD training dataset
└── structures/              # CIF/XYZ/LAMMPS files for Si/SiO₂ systems

dft/                          # Scripts for automating DFT calculations
├── automate_cp2k.py
└── copy_dft.sh

md_setup/                     # Scripts and notebooks for setting up MD jobs
├── frozen_si_interface_example.ipynb
└── md_job_setup.py

models/                       # Trained DeepMD models
├── oxygen_diffusion_model/
│   └── 25-05-13_model_oxygen_diffusion_main.pb
└── preliminary_dataset_model/

structure_generation/         # Code for building interface structures
├── bulk_structure_generator.py
├── si_sio2_generator.py
├── zsl_example_usage.ipynb
└── zsl_generator/
    ├── interface_from_zsl.py
    ├── zsl_analyzer.py
    └── zsl_match.py

templates/                    # Input templates for DFT and MD simulations
├── dft/
└── md/

prep.ipynb                    # Structure preparation and overview notebook
README.md
```

## **Notes**

- All MD simulations use DeepMD models trained on DFT-labeled data.
- DFT calculations are performed using CP2K and are automated for batch processing.
- The interface structures are generated using ZSL matching (via `pymatgen`) and adapted to match amorphous oxide layers.
- The workflow was developed and used for the master’s thesis submitted in July 2025 at NTNU.
