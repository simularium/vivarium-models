import string

import numpy as np
from vivarium.core.engine import Engine

from vivarium_readdy import ReaddyProcess


def radius_for_ix(ix: int):
    return 10.0 + 5.0 * ix


def random_free_particles_state(n_particles, box_size, time_units, spatial_units):
    box_size_3d = np.array([box_size] * 3)
    particles = {}
    letters = list(string.ascii_uppercase)
    random_positions = box_size * (np.random.uniform(size=(n_particles, 3)) - 0.5)
    for p_ix in range(n_particles):
        particles[str(p_ix)] = {
            "type_name": letters[p_ix],
            "position": random_positions[p_ix],
            "radius": radius_for_ix(p_ix),
        }
    return {
        "time_units": time_units,
        "spatial_units": spatial_units,
        "monomers": {
            "box_size": box_size_3d,
            "topologies": {},
            "particles": particles,
        },
    }


def run_readdy_simple_process():
    """
    Run a simulation of particles freely diffusing in ReaDDy.

    Returns:
        The simulation output.
    """
    n_particles = 4
    time_units = "ns"
    spatial_units = "nm"
    box_size = 500.0
    letters = list(string.ascii_uppercase)
    particle_radii = {}
    for p_ix in range(n_particles):
        particle_radii[letters[p_ix]] = radius_for_ix(p_ix)
    readdy_process = ReaddyProcess(
        {
            "time_step": 10000,
            "internal_timestep": 1000,
            "box_size": box_size,
            "periodic_boundary": False,
            "temperature_C": 22.0,
            "viscosity": 8.1,  # cP, cytoplasm
            "force_constant": 250.0,
            "n_cpu": 4,
            "particle_radii": particle_radii,
            "topology_particles": [],
            "reactions": [],
            "time_units": time_units,
            "spatial_units": spatial_units,
        }
    )
    composite = readdy_process.generate()
    engine = Engine(
        composite=composite,
        initial_state=random_free_particles_state(
            n_particles, box_size, time_units, spatial_units
        ),
        emitter="simularium",
    )
    engine.update(200000)
    return engine.emitter.get_data()


def test_readdy_simple_process():
    """
    Test that the process runs correctly.
    This will be executed by pytest.
    """
    output = run_readdy_simple_process()["simularium_converter"]._data
    np.testing.assert_allclose(output.meta_data.box_size, np.array([50.0, 50.0, 50.0]))
    assert output.agent_data.display_data["C"].name == "C"
    np.testing.assert_allclose(
        output.agent_data.times, np.arange(0.0, 200001.0, 10000.0)
    )
    np.testing.assert_allclose(np.unique(output.agent_data.n_agents), np.array([4]))
    assert list(np.unique(output.agent_data.types)) == ["A", "B", "C", "D"]
    np.testing.assert_allclose(
        np.unique(output.agent_data.radii), np.array([1.0, 1.5, 2.0, 2.5])
    )
    assert output.time_units.name == "ns"
    assert output.spatial_units.name == "nm"
    assert output.spatial_units.magnitude == 10.0


if __name__ == "__main__":
    test_readdy_simple_process()
