#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from pymatgen.analysis.interfaces import ZSLGenerator, CoherentInterfaceBuilder


def create_zsl_match(
        substrate,
        substrate_miller,
        film,
        film_miller,
        match_id,
        max_area_ratio_tol=0.09,
        max_area=400,
        max_length_tol=0.03,
        max_angle_tol=0.01,
        bidirectional=False,
):
    # Initialize ZSLGenerator
    zslgen = ZSLGenerator(
        max_area_ratio_tol=max_area_ratio_tol,
        max_area=max_area,
        max_length_tol=max_length_tol,
        max_angle_tol=max_angle_tol,
        bidirectional=bidirectional)

    # Initialize builder
    builder = CoherentInterfaceBuilder(
        substrate_structure=substrate,
        substrate_miller=tuple(substrate_miller),
        film_structure=film,
        film_miller=tuple(film_miller),
        zslgen=zslgen
    )

    # Get ZSLMatch
    zsl_match = builder.zsl_matches[match_id]
    
    print(builder.terminations)

    return zsl_match

