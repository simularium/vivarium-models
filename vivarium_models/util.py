import numpy as np


def agents_update(existing, projected):
    update = {"_add": [], "_delete": []}

    for id, state in projected.items():
        if id in existing:
            update[id] = state
        else:
            update["_add"].append({"key": id, "state": state})

    for existing_id in existing.keys():
        if existing_id not in projected:
            update["_delete"].append(existing_id)

    return update


def create_monomer_update(previous_monomers, new_monomers):
    topologies_update = agents_update(
        previous_monomers["topologies"], new_monomers["topologies"]
    )

    particles_update = agents_update(
        previous_monomers["particles"], new_monomers["particles"]
    )

    return {
        "monomers": {"topologies": topologies_update, "particles": particles_update}
    }


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
