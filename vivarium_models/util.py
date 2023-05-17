import numpy as np


def format_monomer_results(results):
    """
    Workaround since numpy arrays are not preserved in Vivarium?
    """
    monomer_data = list(results.values())[-1]["monomers"]
    formatted_results = {
        "box_center": monomer_data["box_center"],
        "box_size": monomer_data["box_size"],
        "topologies": monomer_data["topologies"],
        "particles": {},
    }
    for particle_id in monomer_data["particles"]:
        particle = monomer_data["particles"][particle_id]
        formatted_results["particles"][particle_id] = {
            "type_name": particle["type_name"],
            "position": np.array(particle["position"]),
            "neighbor_ids": particle["neighbor_ids"],
        }
    return [formatted_results]
