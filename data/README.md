# Data Overview

This folder contains all structure files and datasets used throughout the master's thesis project, including configurations used in training neural network potentials (NNPs) and analyzing oxygen diffusion in Si/SiO₂ interfaces.

---

## `structures/`

Contains selected atomic structures from the project:

- **`asio2/`**  
  Final 80 frames (representing the last 80 ps) of melt-quench simulations of amorphous SiO₂.  
  All simulations started from the same initial configuration but with different random initial velocities.

- **`interfaces/`**  
  Final relaxed Si/SiO₂ interface structures after melting and cooling the SiO₂ region.  
  Includes 10 structures for each Si facet: (100), (110), and (111).

- **`oxygen_diffusion_initial/`**  
  Trajectory outputs from the first round of oxygen diffusion simulations using the **preliminary DeepMD model** trained on the original interface dataset.

- **`oxygen_diffusion_refined_model/`**  
  Trajectories from a second round of diffusion simulations using a **refined DeepMD model**, trained on a dataset expanded with model deviation snapshots and explicit oxygen jump structures.

---

## `deepmd_dataset/`

Contains the training and validation datasets used for training DeepMD models. Each subfolder includes data in DeepMD-compatible format.

- **`preliminary_dataset/`**  
  Initial training dataset constructed during the specialization project.  
  Includes DFT-labeled configurations from the early Si/SiO₂ interface structures.  
  This dataset was used to train the preliminary model (`preliminary_dataset_model`).

- **`model_devi_additions/`**  
  Additional configurations selected based on **model deviation analysis**.  
  Includes both training and validation subsets.  
  These were used to improve model generalization across unexplored regions of configuration space.

- **`oxygen_jumps/`**  
  Structures sampled near manually inserted oxygen defects or hops.  
  These configurations help the model learn the local physics of oxygen migration, and were essential in refining predictions for activation energies.

---

## Notes

- All structures are provided in formats compatible with LAMMPS and CP2K (e.g., `.data`, `.lammpstrj`, `.cif`).
- The datasets under `deepmd_dataset/` were used in combination to train the final NNP model located under `models/oxygen_diffusion_model/`.

