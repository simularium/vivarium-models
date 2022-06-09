#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for actin ReaDDy models
"""

from vivarium_models import ReaddyActinProcess


def test_readdy_actin_process():
    """
    Test the initial ReaDDy actin process
    """
    output = ReaddyActinProcess.run_readdy_actin_process()[5e-09]["monomers"]
    found_monomer = False
    found_dimer = False
    assert len(output["topologies"]) == 2
    for t in output["topologies"]:
        top = output["topologies"][t]
        if top["type_name"] == "Actin-Monomer":
            found_monomer = True
            particle_ids = top["particle_ids"]
            assert len(particle_ids) == 1
            assert (
                "actin#free" in output["particles"][str(particle_ids[0])]["type_name"]
            )
            assert len(output["particles"][str(particle_ids[0])]["neighbor_ids"]) == 0
        if top["type_name"] == "Arp23-Dimer":
            found_dimer = True
            particle_ids = top["particle_ids"]
            assert len(particle_ids) == 2
            assert "arp2" in output["particles"][str(particle_ids[0])]["type_name"]
            assert output["particles"][str(particle_ids[0])]["neighbor_ids"] == [1]
            assert "arp3" in output["particles"][str(particle_ids[1])]["type_name"]
            assert output["particles"][str(particle_ids[1])]["neighbor_ids"] == [0]
    assert found_monomer
    assert found_dimer
