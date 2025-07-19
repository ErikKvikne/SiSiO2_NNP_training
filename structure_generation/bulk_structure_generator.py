import os
import numpy as np
from pymatgen.core import Structure, Lattice
from pymatgen.core.surface import SlabGenerator
from pymatgen.io.xyz import XYZ
from pymatgen.core.interface import fix_pbc


class BulkStructureGenerator:
    """
    A class to generate bulk structures of crystalline silicon (Si) and amorphous silica (SiO₂).
    """

    def __init__(self, unit_cell_length=5.44370237):
        """
        Initializes the generator with default lattice parameters.

        Parameters:
        - unit_cell_length : float, lattice constant for cubic Si (default is 5.44370237 Å).
        """
        self.unit_cell_length = unit_cell_length

    def generate_bulk_si(self, supercell_size=(3, 3, 3)):
        """
        Generates a bulk silicon structure.

        Parameters:
        - supercell_size : tuple, number of unit cells along each axis (default is 3x3x3).

        Returns:
        - pymatgen Structure of bulk Si.
        """
        si_bulk = Structure.from_spacegroup(
            227,
            Lattice.cubic(self.unit_cell_length),
            ["Si"],
            [[0, 0, 0]]
        )

        # Create a supercell if needed
        si_bulk.make_supercell(supercell_size)
        return si_bulk

    def generate_bulk_sio2(self, asio2_id):
        """
        Loads an amorphous SiO₂ structure from file.

        Parameters:
        - asio2_id : int, ID of the a-SiO₂ structure (e.g., 1, 2, 3...).

        Returns:
        - pymatgen Structure of bulk a-SiO₂.
        """
        structure_folder_path = "/Users/erik/Desktop/10_semester/master_thesis/data/structures/asio2_structures_ini/"

        # Identify which structure files exist
        valid_numbers = {
            int(f.split("_")[1])  # Extract ID from filename "asio2_001_pre.xyz" -> 1
            for f in os.listdir(structure_folder_path)
            if f.startswith("asio2_") and f.endswith("_pre.xyz")
        }

        if asio2_id not in valid_numbers:
            raise ValueError(f"Invalid asio2 ID: {asio2_id}. "
                             f"Available IDs are: {sorted(valid_numbers)}")

        # Construct the filename of the chosen a-SiO₂
        filename = f"asio2_{str(asio2_id).zfill(3)}_pre.xyz"
        filepath = os.path.join(structure_folder_path, filename)

        # Read the second line to get the cell dimensions
        with open(filepath, "r") as file:
            lines = file.readlines()
            cell_dimensions = list(map(float, lines[1].split()))
        if len(cell_dimensions) != 3:
            raise ValueError(f"Cell dimension line in {filename} must have exactly 3 floats. "
                             f"Got: {cell_dimensions}")

        # Construct the lattice from these parameters
        lattice = Lattice.from_parameters(*cell_dimensions, 90, 90, 90)

        # Load molecular positions from XYZ (ignoring the first two lines)
        asio2_molecule = XYZ.from_file(filepath).molecule

        # Build a pymatgen Structure
        asio2_structure = Structure(
            lattice,
            asio2_molecule.species,
            asio2_molecule.cart_coords,
            coords_are_cartesian=True
        )

        return asio2_structure

