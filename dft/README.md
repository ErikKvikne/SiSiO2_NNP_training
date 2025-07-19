# Density Functional Theory (DFT) Automation

This folder contains scripts used to automate the preparation and submission of **CP2K** DFT calculations based on atomic configurations extracted from MD simulations. The workflow streamlines the process of selecting snapshots, converting them to appropriate formats, generating input files, and launching jobs on HPC systems.

## Contents

### `automate_cp2k.py`

A Python script that automates the DFT input preparation pipeline for a set of MD simulations. Its main features include:

- **MD Run Validation**: Verifies simulation success by checking `.err` files.
- **Snapshot Handling**:
  - Extracts specific timesteps from `snapshot.lammpstrj` trajectory files.
  - Converts atomic coordinates into CIF format with correct lattice parameters.
- **CP2K Input Generation**:
  - Fills a CP2K input template with simulation-specific filenames and parameters.
  - Generates job-specific SLURM `submit.sh` scripts.
- **Job Launcher Script**:
  - Writes a global `launch_all_jobs.sh` file for submitting all generated jobs efficiently.

This tool was used to extract representative snapshots (from MD simulations involving Si/SiO₂ interfaces) and compute their energies and forces for training neural network potentials.

> The default CP2K input template path is hardcoded (`/users/ekvikne/automate/cp2k_input_template.inp`) and should be adjusted to match your environment.

---

### `copy_dft.sh`

A simple shell script that uses `rsync` to copy DFT simulation folders from the **Puhti** supercomputer to a local machine, excluding large files (e.g., wavefunction files `.wfn`) to reduce transfer size.

#### Usage
```bash
./copy_dft.sh <remote_full_path> <local_destination>
```
Example:
```bash
./copy_dft.sh /scratch/jeakola/ekvikne/deepmd/test_run /Users/erik/Desktop/dft_results/
```

---

## Notes

- The DFT snapshots generated through this workflow were used to evaluate energies and forces with **CP2K**, forming the basis for the training of DeepMD models.
- Ensure your environment modules (e.g., `gcc`, `openmpi`, `cp2k`) and submission configurations match the ones defined in the generated SLURM scripts.

This automation was critical in scaling DFT reference generation for larger datasets and in maintaining consistency across simulation runs.
