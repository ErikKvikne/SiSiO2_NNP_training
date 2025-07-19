# Molecular Dynamics Setup

This folder contains tools and examples for setting up Molecular Dynamics (MD) simulations of Si/SiO₂ interface systems using DeepMD-trained neural network potentials in LAMMPS.

## Contents

### `frozen_si_interface_example.ipynb`
A complete, minimal working example notebook that demonstrates how to prepare and generate MD input files for simulating oxygen diffusion in Si/SiO₂ interfaces. It automates:

- Heating, equilibration, and cooling of the amorphous SiO₂ region
- Selective freezing and unfreezing of the crystalline Si region
- Controlled thermal protocols using the NPT ensemble (pressure control along the z-axis)
- Generation of multiple independent simulation folders (`run_01/`, `run_02/`, etc.) with randomized seeds
- Creation of both `in.lammps` (input script) and `submit.sh` (SLURM job script) for each run


### `md_job_setup.py`
A modular Python script for batch generation of LAMMPS-ready MD job folders from a directory containing `.cif` or `.data` structure files. Core functionality includes:

- Converts `.cif` structures to `.data` format using ASE, or copies existing `.data` files
- Automatically creates job folders named after the structure and temperature (e.g., `my_structure_T1500`)
- Fills in user-defined `in.lammps` and `submit.sh` templates
- Generates a `launch_all_jobs.sh` script to conveniently submit all generated jobs

This tool was used to automate MD runs across different temperatures and interface structures.

---

## Notes

- The default paths in both files assume a DeepMD environment and specific cluster setup. Adjust `structure_file`, model paths, and SLURM parameters to fit your environment.
- Template files used by `md_job_setup.py` (e.g., `in.lammps.template`, `submit.sh.template`) are located in `templates/md/`.

These scripts supported large-scale and reproducible simulation workflows, reducing manual setup effort during both development and production phases of the thesis.
