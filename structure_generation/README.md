# Structure Generation

This folder contains the main structure generation utilities used in the master's thesis for creating crystalline and amorphous silicon dioxide (SiO₂) structures and Si/SiO₂ interface models. These tools were used both in the early stages of dataset generation and in later refinement of simulation-ready interface configurations.

## Contents

### `bulk_structure_generator.py`
Defines a `BulkStructureGenerator` class used to:
- Generate crystalline bulk silicon (Si) structures by specifying the lattice constant and supercell dimensions.
- Load amorphous SiO₂ structures (`asio2`) from `.xyz` files with cell parameters embedded in the second line.
  
This was particularly useful for standardizing and validating the external amorphous SiO₂ structures received for the project, and for building clean cubic supercells of crystalline silicon.

---

### `si_sio2_generator.py`
Defines a `SiSiO2InterfaceGenerator` class for constructing combined Si/SiO₂ interfaces. Key capabilities:
- Load and shift amorphous SiO₂ structures.
- Generate Si slabs of specified Miller indices and thickness.
- Scale the Si slab in-plane to match the amorphous oxide.
- Stack and optionally modify the interface (e.g., indent and back-fill regions).
- Output simulation-ready structures (e.g., `.cif` files).

This was used to generate the preliminary training set structures and analyze different interface configurations.

---

### `zsl_generator/`

This subfolder contains tools for generating coherent Si/SiO₂ interfaces using ZSL (Zur–Sayre–Levine) lattice matching, based on `pymatgen`'s `ZSLGenerator` and `CoherentInterfaceBuilder`.

- `zsl_match.py`  
  Defines a utility function (`create_zsl_match`) that computes and returns a specific ZSL match between a substrate and film given their Miller indices. Used as a lightweight front-end to the matching engine.

- `zsl_analyzer.py`  
  Performs full match generation with specified geometric tolerances (area, angle, length). Computes strain measures (e.g., von Mises strain) and saves all matches with relevant metadata to `.csv` and `.json` formats. Useful for screening and selecting optimal lattice matches.

- `interface_from_zsl.py`  
  Constructs the actual atomic interface structure using a selected ZSL match. Handles vacuum insertion, termination, slab thickness, atom removal beyond bounds, and optional substrate flipping. Returns a `pymatgen` `Interface` object suitable for simulation or visualization.

---

### `zsl_example_usage.ipynb`

This Jupyter notebook demonstrates the full pipeline for constructing lattice-matched Si/SiO₂ interfaces using the ZSL framework. It showcases how to use the tools in `zsl_generator/` for matching, analyzing, and building atomic interface structures based on Materials Project data.

#### Main Features:
- **Retrieves bulk structures** for Si and α-quartz SiO₂ from the Materials Project using `MPRester`.
- **Computes ZSL matches** between the Si substrate and SiO₂ film using `compute_zsl_matches`, storing metadata and strain analysis.
- **Selects a specific match** using `create_zsl_match`, with printed available terminations.
- **Builds the interface** using `interface_from_zsl`, allowing control over gap spacing, slab thickness, vacuum, substrate flipping, and alignment.
- **Saves the final interface** as `.cif` and LAMMPS `.data` files using ASE, with a filename generated based on parameters for clarity and reproducibility.

This example serves as a reference for how to generate high-quality, lattice-matched interfaces suitable for DFT or NNP simulations.


---

## Notes

- All interfaces are aligned along the z-axis, with periodic boundary conditions.
- Scripts in this folder are used both for generating training data and for validating structural motifs relevant to the thesis work.
