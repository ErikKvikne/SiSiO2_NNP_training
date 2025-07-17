#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Currently only works with numpy<1.24.0
"""

import shutil
import numpy as np
import pandas as pd
from pathlib import Path
from pymatgen.analysis.interfaces import CoherentInterfaceBuilder, ZSLGenerator
from pymatgen.analysis.interfaces.zsl import vec_area
from pymatgen.analysis.elasticity.strain import Deformation
from ase.parallel import world
from monty.json import MontyEncoder
import json

DATA_PATH = Path('/Users/erik/Desktop/10_semester/master_thesis/data/structures/matches')


def compute_zsl_matches(substrate, substrate_miller, film, film_miller, calc_name, max_area_ratio_tol=0.09,
                        max_area=400, max_length_tol=0.03, max_angle_tol=0.01, bidirectional=False, metadata=None):

    # Directory to store data
    calc_path = DATA_PATH / 'zsl_analyzer' / calc_name

    # Initialize directory
    if calc_path.exists():
        shutil.rmtree(calc_path)
    if not calc_path.exists():
        if world.rank == 0:
            calc_path.mkdir(exist_ok=False)

    # Save metadata
    if metadata is not None:
        with open(calc_path / "01_Metadata.txt", 'w') as f:
            f.write(metadata)

    # Initialize interface builder
    zslgen = ZSLGenerator(max_area_ratio_tol=max_area_ratio_tol, max_area=max_area, max_length_tol=max_length_tol,
                          max_angle_tol=max_angle_tol, bidirectional=bidirectional)
    builder = CoherentInterfaceBuilder(substrate_structure=substrate,
                                       substrate_miller=substrate_miller,
                                       film_structure=film,
                                       film_miller=film_miller,
                                       zslgen=zslgen)

    # Create dataframe for match data
    zsl_match_data = pd.DataFrame(columns=['id', 'substrate_miller', 'film_miller', 'match_area', 'von_mises_strain',
                                           'substrate_area', 'film_area', 'substrate_sl_area', 'film_sl_area',
                                           'substrate_v1', 'substrate_v2', 'film_v1', 'film_v2',
                                           'substrate_area_ratio', 'film_area_ratio',
                                           'substrate_transformation', 'film_transformation',
                                           'sl_a', 'sl_b']).set_index('id')

    # Loop over matches
    for idx, m in enumerate(builder.zsl_matches):

        # Get strain
        dfm = Deformation(m.match_transformation)
        strain = dfm.green_lagrange_strain

        # Save match data to dataframe
        match_data = pd.Series({
            'substrate_miller': str(substrate_miller),
            'film_miller': str(film_miller),
            'match_area': m.match_area,
            'von_mises_strain': strain.von_mises_strain,
            'substrate_area': vec_area(*m.substrate_vectors),
            'film_area': vec_area(*m.film_vectors),
            'substrate_sl_area': vec_area(*m.substrate_sl_vectors),
            'film_sl_area': vec_area(*m.film_sl_vectors),
            'substrate_v1': str(m.substrate_vectors[0].round(2)),
            'substrate_v2': str(m.substrate_vectors[1].round(2)),
            'film_v1': str(m.film_vectors[0].round(2)),
            'film_v2': str(m.film_vectors[1].round(2)),
            'substrate_area_ratio': m.match_area / vec_area(*m.substrate_vectors),
            'film_area_ratio': m.match_area / vec_area(*m.film_vectors),
            'substrate_transformation': str(m.substrate_transformation),
            'film_transformation': str(m.film_transformation),
            'sl_a': np.linalg.norm(m.substrate_sl_vectors[0]),
            'sl_b': np.linalg.norm(m.substrate_sl_vectors[1]),
        })
        zsl_match_data.loc[idx] = pd.Series(match_data)

        # Save match
        if world.rank == 0:
            with open(calc_path / f"{idx}.json", 'w') as f:
                json.dump(m, f, cls=MontyEncoder)

    # Save match data to file
    if world.rank == 0:
        zsl_match_data.to_csv(calc_path / ("00_"+calc_name+".csv"))
