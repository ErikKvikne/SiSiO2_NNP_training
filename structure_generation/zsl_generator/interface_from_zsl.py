#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np
import math
from pymatgen.core import DummySpecies, Element, Structure
from pymatgen.analysis.interfaces import CoherentInterfaceBuilder, ZSLMatch
from pymatgen.core.interface import Interface
from pymatgen.io.ase import AseAtomsAdaptor
from pymatgen.analysis.interfaces.zsl import vec_area
import json


def interface_from_zsl(
        substrate,
        substrate_miller,
        film,
        film_miller,
        zsl_match,
        termination,
        gap,
        vacuum_over_film,
        film_thickness,
        film_shift,
        substrate_thickness,
        substrate_shift,
        in_plane_offset,
        substrate_flip,
):

    # Initialize builder
    if 'kind_name' in substrate.site_properties:
        for i, n in enumerate(substrate.site_properties['kind_name']):
            if any(char.isdigit() for char in n):
                substrate.replace(i, DummySpecies(f'!{n}'))
    if 'kind_name' in film.site_properties:
        for i, n in enumerate(film.site_properties['kind_name']):
            if any(char.isdigit() for char in n):
                film.replace(i, DummySpecies(f'!{n}'))

    builder = CoherentInterfaceBuilder(
        substrate_structure=substrate,
        substrate_miller=substrate_miller,
        film_structure=film,
        film_miller=film_miller,
    )

    # Replace matches with the one requested
    builder.zsl_matches = [zsl_match]

    # Print data
    match_data = {
        'substrate_miller': str(substrate_miller),
        'film_miller': str(film_miller),
        'match_area': zsl_match.match_area,
        'substrate_area': vec_area(*zsl_match.substrate_vectors),
        'film_area': vec_area(*zsl_match.film_vectors),
        'substrate_sl_area': vec_area(*zsl_match.substrate_sl_vectors),
        'film_sl_area': vec_area(*zsl_match.film_sl_vectors),
        'substrate_v1': str(np.array(zsl_match.substrate_vectors[0]).round(2)),
        'substrate_v2': str(np.array(zsl_match.substrate_vectors[1]).round(2)),
        'film_v1': str(np.array(zsl_match.film_vectors[0]).round(2)),
        'film_v2': str(np.array(zsl_match.film_vectors[1]).round(2)),
        'substrate_sl_v1': str(np.array(zsl_match.substrate_sl_vectors[0]).round(2)),
        'substrate_sl_v2': str(np.array(zsl_match.substrate_sl_vectors[1]).round(2)),
        'film_sl_v1': str(np.array(zsl_match.film_sl_vectors[0]).round(2)),
        'film_sl_v2': str(np.array(zsl_match.film_sl_vectors[1]).round(2)),
        'substrate_area_ratio': zsl_match.match_area / vec_area(*zsl_match.substrate_vectors),
        'film_area_ratio': zsl_match.match_area / vec_area(*zsl_match.film_vectors),
        #'twisting_angle1': vec_angle(np.array(match.substrate_vectors[0]), np.array(match.substrate_sl_vectors[0])),
        #'twisting_angle2': vec_angle(np.array(match.substrate_vectors[1]), np.array(match.substrate_sl_vectors[1]))
    }

    # Build the interface
    interface = next(
        builder.get_interfaces(
            termination=termination,
            gap=gap,
            vacuum_over_film=vacuum_over_film+10,
            film_thickness=film_thickness+film_shift+1,
            substrate_thickness=substrate_thickness+substrate_shift+1,
            in_layers=True,
        )
    )

    # Update in plane offset
    interface.in_plane_offset = in_plane_offset

    # Shift and remove extra film sites
    film_d = film.lattice.d_hkl(tuple(film_miller))
    film_min_z = min([site.coords[2] for site in interface.film_sites])
    interface.translate_sites(interface.film_indices, (0, 0, -film_d*film_shift), frac_coords=False, to_unit_cell=False)
    film_max_z = film_min_z + film_d*film_thickness
    excess_film_sites = [i for i, site in enumerate(interface.sites)
                         if ((site.coords[2] >= film_max_z-1e-8) or (site.coords[2] < film_min_z-1e-8)) and
                         site.properties['interface_label'] == 'film']
    interface.remove_sites(excess_film_sites)

    # Remove extra substrate sites
    substrate_d = substrate.lattice.d_hkl(tuple(substrate_miller))
    substrate_max_z = max([site.coords[2] for site in interface.substrate_sites])
    interface.translate_sites(interface.substrate_indices, (0, 0, +substrate_d*substrate_shift), frac_coords=False, to_unit_cell=False)
    substrate_min_z = substrate_max_z - substrate_d*substrate_thickness
    excess_substrate_sites = [i for i, site in enumerate(interface.sites)
                              if ((site.coords[2] <= substrate_min_z+1e-8) or (site.coords[2] > substrate_max_z+1e-8)) and
                              site.properties['interface_label'] == 'substrate']
    interface.remove_sites(excess_substrate_sites)

    substrate_slab = interface.substrate
    film_slab = interface.film
    if substrate_flip:
        coords = substrate_slab.cart_coords
        coords[:, 2] = -coords[:, 2]
        substrate_slab = Structure(lattice=substrate_slab.lattice, species=substrate_slab.species, coords=coords, coords_are_cartesian=True)

    # Update lattice
    interface = Interface.from_slabs(
        substrate_slab=substrate_slab,
        film_slab=film_slab,
        in_plane_offset=in_plane_offset,  # This parameter does not effect the positions of the atoms, only sets the value of the parameter
        gap=gap,
        vacuum_over_film=vacuum_over_film,
        interface_properties=interface.interface_properties,
    )


    kind_names = list()
    for i, s in enumerate(interface.species):
        if any(char.isdigit() for char in s.symbol):
            interface.replace(i, Element(s.symbol[1:-1]), properties={'interface_label': interface.site_properties['interface_label'][i]})
            kind_names.append(s.symbol[1:])
        else:
            kind_names.append(s.symbol)
    interface.add_site_property('kind_name', kind_names)

    return interface

