import os
import numpy as np
from scipy.spatial.distance import cdist
from ase.visualize import view
from pymatgen.core import Structure, Lattice
from pymatgen.core.surface import SlabGenerator
from pymatgen.io.xyz import XYZ
from pymatgen.core.interface import fix_pbc

class SiSiO2InterfaceGenerator:
    """
    A class to generate Si/SiO2 interfaces from amorphous SiO2 (a-SiO2) and crystalline Si slabs.
    Incorporates functionality for:
      - Loading a-SiO2 structures by ID (reading lattice parameters from the file).
      - Generating Si slabs with specified Miller indices and thickness.
      - Combining them into a single interface.
      - Introducing indentations in either Si or a-SiO2, optionally back-filled with atoms
        from the other structure (avoiding collisions).
    """

    def __init__(self,
                 miller_index,
                 min_thickness,
                 asio2_id,
                 asio2_shift=None,
                 unit_cell_length=5.44370237):
        """
        Initializes the generator with Si and a-SiO2 structures.

        Parameters:
        - miller_index      : tuple(int, int, int), Miller index for the Si slab.
        - min_thickness     : float, minimum thickness of the Si slab (Å).
        - asio2_id          : int, ID of the a-SiO2 structure (e.g. 1, 2, 3...).
        - asio2_shift       : list of floats, fractional shift [sx, sy, sz] for the a-SiO2 lattice.
        - unit_cell_length  : float, default is 5.44370237 Å (approx. Si lattice const).
        """
        self.miller_index = miller_index
        self.min_thickness = min_thickness
        self.unit_cell_length = unit_cell_length
        self.asio2_shift = asio2_shift if asio2_shift else [0, 0, 0]

        # Fetch the amorphous SiO2 structure
        self.asio2 = self._fetch_asio2(asio2_id)

        # Generate the Si slab (scaled to match a-SiO2 in-plane dimensions)
        self.si_slab = self._generate_si_slab()

    def _fetch_asio2(self, asio2_id):
        """
        Fetches the amorphous SiO2 structure by ID, reading lattice dimensions
        from the second line of the .xyz file and applying the given fractional shift.

        Parameters:
        - asio2_id : int, the ID of the SiO2 structure to fetch (e.g., 1, 2, 3...).

        Returns:
        - asio2_structure: pymatgen Structure for the chosen a-SiO2.
        """
        structure_folder_path = "/Users/erik/Desktop/10_semester/master_thesis/data/structures/asio2_structures_ini/"

        # Identify which structure files exist
        valid_numbers = {
            int(f.split("_")[1])  # e.g. from "asio2_001_pre.xyz" -> 1
            for f in os.listdir(structure_folder_path)
            if f.startswith("asio2_") and f.endswith("_pre.xyz")
        }

        if asio2_id not in valid_numbers:
            raise ValueError(f"Invalid asio2 ID: {asio2_id}. "
                             f"Available IDs are: {sorted(valid_numbers)}")

        # Construct the filename of the chosen a-SiO2
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

        # Load the molecular positions from the XYZ (ignoring the first two lines)
        asio2_molecule = XYZ.from_file(filepath).molecule

        # Build a pymatgen Structure
        asio2_structure = Structure(
            lattice,
            asio2_molecule.species,
            asio2_molecule.cart_coords,
            coords_are_cartesian=True
        )

        # Apply the fractional shift
        shift_cartesian = np.array(self.asio2_shift) * np.array([lattice.a, lattice.b, lattice.c])
        asio2_structure.translate_sites(
            range(len(asio2_structure)),
            shift_cartesian,
            frac_coords=False,
            to_unit_cell=True
        )

        return asio2_structure

    def _generate_si_slab(self):
        """
        Generates a silicon slab with the specified Miller index and thickness,
        optionally scaling it in-plane to match the a-SiO2 lattice dimensions.

        Returns:
        - supercell : pymatgen Structure (the scaled Si slab).
        """
        # Create conventional Si bulk
        si_bulk = Structure.from_spacegroup(
            227,
            Lattice.cubic(self.unit_cell_length),
            ["Si"],
            [[0, 0, 0]]
        )

        # Generate slab (no vacuum, since we combine with a-SiO2)
        slabgen = SlabGenerator(
            si_bulk,
            self.miller_index,
            min_slab_size=self.min_thickness,
            min_vacuum_size=0,
            center_slab=False,
            primitive=False,
            lll_reduce=True
        )
        slab = slabgen.get_slab()
        # Orthogonalize and fix PBC
        slab_ortho = fix_pbc(slab.get_orthogonal_c_slab().get_sorted_structure())

        # Scale the slab to match the a-SiO2 in-plane dimensions
        if self.asio2 is None:
            # Fallback
            scaling_matrix = [1, 1, 1]
        else:
            # Compare the a,b lattice lengths
            si_a, si_b = slab_ortho.lattice.a, slab_ortho.lattice.b
            asio2_a, asio2_b = self.asio2.lattice.a, self.asio2.lattice.b

            repeat_a = int(round(asio2_a / si_a))
            repeat_b = int(round(asio2_b / si_b))
            scaling_matrix = [[repeat_a, 0, 0],
                              [0, repeat_b, 0],
                              [0, 0, 1]]

        # Make the supercell
        supercell = slab_ortho.copy()
        supercell.make_supercell(scaling_matrix)
        return supercell

    def generate_interface(self, filename = None, vacuum_separation=0, vacuum_over=0):
        """
        Builds the combined Si/SiO2 interface along the c-axis, with optional vacuum separation,
        then saves the result in CIF format and opens an ASE viewer window.

        Parameters:
        - filename          : str, path to save the interface CIF file (e.g. "interface.cif").
        - vacuum_separation : float, gap between the Si slab and a-SiO2 (Å).
        - vacuum_over       : float, additional vacuum above the top a-SiO2 region (Å).
        """
        # The in-plane lengths are the max of the two lattices, c is sum + vacuum
        combined_lattice = Lattice.from_parameters(
            max(self.si_slab.lattice.a, self.asio2.lattice.a),
            max(self.si_slab.lattice.b, self.asio2.lattice.b),
            self.si_slab.lattice.c + self.asio2.lattice.c + vacuum_separation + vacuum_over,
            90, 90, 90
        )

        # Start with the Si slab positions
        combined_structure = Structure(
            combined_lattice,
            self.si_slab.species,
            self.si_slab.cart_coords,
            coords_are_cartesian=True
        )

        # Shift the a-SiO2 block so it sits on top of the Si slab plus vacuum
        for site in self.asio2:
            combined_structure.append(
                site.specie,
                site.coords + [0, 0, self.si_slab.lattice.c + vacuum_separation],
                coords_are_cartesian=True
            )

        if filename:
            # Write structure to file
            combined_structure.to(filename, fmt="cif")
            print(f"Interface saved as {filename}")

        else:
            # Return structure
            return combined_structure

    def indent(self,
               x_int,
               y_int,
               si_indent=True,
               fill_indent=False,
               si_si_threshold=2.3,
               si_o_threshold=1.55):
        """
        Introduces an indentation in either the Si slab or in the a-SiO2 region.
        Optionally fills that indentation with atoms from the other structure
        (while checking distance thresholds to avoid overlaps).

        Parameters:
        - x_int, y_int      : float, the integer coordinates (in multiples of 'unit_cell_length')
                              indicating where the indentation region starts in x and y.
        - si_indent         : bool, True => indent in the Si slab. False => indent in a-SiO2.
        - fill_indent       : bool, if True, tries to fill that void with atoms from the other structure.
        - si_si_threshold   : float, minimal allowed Si-Si distance when refilling.
        - si_o_threshold    : float, minimal allowed Si-O distance when refilling.
        """
        delta = 0.001
        ucl = self.unit_cell_length  # For readability

        if si_indent:
            # Indent from top of Si (z from [z0 - ucl, z0])
            lower_bounds = [x_int * ucl - delta,
                            y_int * ucl - delta,
                            self.si_slab.lattice.c - ucl - delta]
            upper_bounds = [x_int * ucl + ucl - delta,
                            y_int * ucl + ucl - delta,
                            self.si_slab.lattice.c - delta]

            cart_coords_si = np.array(self.si_slab.cart_coords)
            indices_to_remove = [
                i for i, coord in enumerate(cart_coords_si)
                if all(lower_bounds <= coord) and all(coord <= upper_bounds)
            ]
            self.si_slab.remove_sites(indices_to_remove)

            if fill_indent:
                # Fill from the a-SiO2 structure
                lower_bounds_asio2 = [x_int * ucl - delta,
                                      y_int * ucl - delta,
                                      self.asio2.lattice.c - ucl - delta]
                upper_bounds_asio2 = [x_int * ucl + ucl - delta,
                                      y_int * ucl + ucl - delta,
                                      self.asio2.lattice.c - delta]

                cart_coords_asio2 = np.array(self.asio2.cart_coords)
                indices_to_add = [
                    i for i, coord in enumerate(cart_coords_asio2)
                    if all(lower_bounds_asio2 <= coord) and all(coord <= upper_bounds_asio2)
                ]
                coords_to_add_asio2_frame = [cart_coords_asio2[i] for i in indices_to_add]
                # Shift them up to Si’s coordinate frame
                coords_to_add = [
                    [x, y, z - self.asio2.lattice.c + self.si_slab.lattice.c]
                    for (x, y, z) in coords_to_add_asio2_frame
                ]
                species_to_add = [self.asio2.species[i] for i in indices_to_add]

                for idx, atom_coord in enumerate(coords_to_add):
                    distances = cdist([atom_coord], np.array(self.si_slab.cart_coords))
                    if distances.size > 0:
                        min_distance = distances.min()
                        symbol = species_to_add[idx].symbol
                        threshold = si_si_threshold if symbol == "Si" else si_o_threshold
                        if min_distance < threshold:
                            # Overlaps => skip
                            continue
                    self.si_slab.append(species_to_add[idx], atom_coord, coords_are_cartesian=True)
        else:
            # Indent from bottom of the a-SiO2 region (z from [0, ucl]) or wherever it sits
            lower_bounds = [x_int * ucl - delta,
                            y_int * ucl - delta,
                            -delta]
            upper_bounds = [x_int * ucl + ucl - delta,
                            y_int * ucl + ucl - delta,
                            ucl - delta]

            cart_coords_asio2 = np.array(self.asio2.cart_coords)
            indices_to_remove = [
                i for i, coord in enumerate(cart_coords_asio2)
                if all(lower_bounds <= coord) and all(coord <= upper_bounds)
            ]
            self.asio2.remove_sites(indices_to_remove)

            if fill_indent:
                # Fill from the Si slab
                lower_bounds_si = [x_int * ucl - delta,
                                   y_int * ucl - delta,
                                   -delta]
                upper_bounds_si = [x_int * ucl + ucl - delta,
                                   y_int * ucl + ucl - delta,
                                   ucl - delta]
                cart_coords_si = np.array(self.si_slab.cart_coords)
                indices_to_add = [
                    i for i, coord in enumerate(cart_coords_si)
                    if all(lower_bounds_si <= coord) and all(coord <= upper_bounds_si)
                ]
                coords_to_add_si_frame = [cart_coords_si[i] for i in indices_to_add]
                species_to_add = [self.si_slab.species[i] for i in indices_to_add]

                for idx, atom_coord in enumerate(coords_to_add_si_frame):
                    # Insert into a-SiO2
                    self.asio2.append(species_to_add[idx], atom_coord, coords_are_cartesian=True)
                    new_atom_index = len(self.asio2) - 1
                    # Check for collisions with existing a-SiO2 atoms
                    distances = cdist([self.asio2[new_atom_index].coords],
                                      np.array(self.asio2.cart_coords[:-1]))
                    indices_close = []
                    for j, dist_val in enumerate(distances[0]):
                        symbol = self.asio2.species[j].symbol
                        if symbol == "Si" and dist_val < si_si_threshold:
                            indices_close.append(j)
                        elif symbol == "O" and dist_val < si_o_threshold:
                            indices_close.append(j)
                    # Remove overlapping atoms
                    if indices_close:
                        self.asio2.remove_sites(indices_close)

        print("Indentation applied.")
