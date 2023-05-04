import os
import string

from vivarium.core.process import Process
from vivarium.core.directories import PROCESS_OUT_DIR
from vivarium.core.engine import Engine

import numpy as np
import readdy
from tqdm import tqdm

from subcell_analysis.readdy import ReaddyUtil
from vivarium_models.util import create_monomer_update, monomer_ports_schema

NAME = "ReaDDy_simple"


class ReaddySimpleProcess(Process):
    """
    This process uses ReaDDy to model 4 diffusing particles.
    """

    name = NAME

    defaults = {
        "n_particles" : 4,
        "box_size" : 500.,  # nm
        "temperature_C" : 22.0,
        "viscosity" : 8.1,  # cP
        "periodic_boundary" : False,
        "force_constant" : 250.,
        "internal_timestep" : 0.1,  # ns
    }


    def __init__(self, parameters=None):
        super(ReaddySimpleProcess, self).__init__(parameters)
        self.create_system()
        

    def calculate_diffusionCoefficient(self, radius):
        """
        calculates the theoretical diffusion constant of a spherical particle
        in a media with viscosity [cP] at temperature [Kelvin].
            with radius radius[nm]

            returns nm^2/s
        """
        return (
            (1.38065 * 10 ** (-23) * self.parameters["temperature_K"])
            / (6 * np.pi * self.parameters["viscosity"] * 10 ** (-3) * radius * 10 ** (-9))
            * 10**18
            / 10**9
        )


    def create_system(self):
        """
        Create a ReaDDy system with the given number of 
        types of particles freely diffusing in a box.
        """
        # create readdy system
        box_size_3d = np.array([self.parameters["box_size"]] * 3)
        self.readdy_system = readdy.ReactionDiffusionSystem(
            box_size=box_size_3d,
            periodic_boundary_conditions=[self.parameters["periodic_boundary"]] * 3,
        )
        self.parameters["temperature_K"] = self.parameters["temperature_C"] + 273.15
        self.readdy_system.temperature = self.parameters["temperature_K"]
        
        # add particle species
        letters = list(string.ascii_uppercase)
        for p_ix in range(self.parameters["n_particles"]):
            diffCoeff = self.calculate_diffusionCoefficient(1. + 0.5 * p_ix)  # nm^2/s
            self.readdy_system.add_topology_species(letters[p_ix], diffCoeff)
            
        # add repulsion potentials for excluded volume
        for p_ix1 in range(self.parameters["n_particles"]):
            for p_ix2 in range(p_ix1 + 1, self.parameters["n_particles"]):
                self.readdy_system.potentials.add_harmonic_repulsion(
                    particle_type1=letters[p_ix1], 
                    particle_type2=letters[p_ix2], 
                    force_constant=self.parameters["force_constant"], 
                    interaction_distance=1.5 + 0.5 * (p_ix1 + p_ix2),
                )
        
        # add box potential if no periodic boundary
        if not self.parameters["periodic_boundary"]:
            box_potential_size = box_size_3d - 2.0
            for particle_type in letters[:self.parameters["n_particles"]]:
                self.readdy_system.potentials.add_box(
                    particle_type=particle_type,
                    force_constant=self.parameters["force_constant"],
                    origin=-0.5 * box_potential_size,
                    extent=box_potential_size,
                )


    def ports_schema(self):
        return monomer_ports_schema

    
    def create_simulation_with_particles(self, particles):
        self.readdy_simulation = self.readdy_system.simulation("CPU")
        for p_id in particles:
            self.readdy_simulation.add_particle(
                type=particles[p_id]["type_name"], 
                position=particles[p_id]["position"], 
            )

    def simulate_readdy(self, timestep):
        """
        Simulate in ReaDDy for the given timestep
        """
        def loop():
            readdy_actions = self.readdy_simulation._actions
            init = readdy_actions.initialize_kernel()
            diffuse = readdy_actions.integrator_euler_brownian_dynamics(
                self.parameters["internal_timestep"]
            )
            calculate_forces = readdy_actions.calculate_forces()
            create_nl = readdy_actions.create_neighbor_list(
                self.readdy_system.calculate_max_cutoff().magnitude
            )
            update_nl = readdy_actions.update_neighbor_list()
            react = readdy_actions.reaction_handler_uncontrolled_approximation(
                self.parameters["internal_timestep"]
            )
            observe = readdy_actions.evaluate_observables()
            init()
            create_nl()
            calculate_forces()
            update_nl()
            observe(0)
            n_steps = int(timestep / self.parameters["internal_timestep"])
            for t in tqdm(range(1, n_steps + 1)):
                diffuse()
                update_nl()
                react()
                update_nl()
                calculate_forces()
                observe(t)

        self.readdy_simulation._run_custom_loop(loop, show_summary=False)
    
    
    def get_particles_from_simulation(self):
        result = {
            "box_center" : np.zeros(3),
            "box_size" : self.parameters["box_size"],
            "topologies": {},
            "particles": {},
        }
        for particle in self.readdy_simulation.current_particles:
            result["particles"][str(particle.id)] = {
                "type_name" : particle.type,
                "position" : particle.pos,
            }
        return result


    def next_update(self, timestep, states):
        print(f"ReaDDy simple process updating by {timestep} ns")
        
        self.create_simulation_with_particles(states["monomers"]["particles"])
        self.simulate_readdy(timestep)
        new_monomers = self.get_particles_from_simulation()

        return create_monomer_update(states["monomers"], new_monomers)

        
def random_initial_state(parameters):
    result = {
        "box_center" : np.zeros(3),
        "box_size" : parameters["box_size"],
        "topologies": {},
        "particles": {},
    }
    letters = list(string.ascii_uppercase)
    random_positions = (
        parameters["box_size"] *
        (np.random.uniform(size=(parameters["n_particles"], 3)) - 0.5)
    )
    for p_ix in range(parameters["n_particles"]):
        result["particles"][str(p_ix)] = {
            "type_name" : letters[p_ix],
            "position" : random_positions[p_ix],
        }
    return {"monomers" : result}


# functions to configure and run the process
def run_readdy_simple_process():
    """
    Run a simulation of the process.

    Returns:
        The simulation output.
    """
    readdy_process = ReaddySimpleProcess()
    composite = readdy_process.generate()
    initial_state = random_initial_state(readdy_process.parameters)
    
    sim = Engine(composite=composite, initial_state=initial_state)
    
    sim.update(10)  # ns
    
    output = sim.emitter.get_timeseries()
    return output


def test_readdy_simple_process():
    '''
    Test that the process runs correctly.
    This will be executed by pytest.
    '''
    output = run_readdy_simple_process()
    # TODO: Add assert statements to ensure correct performance.


def main():
    '''Simulate the process and plot results.'''
    # make an output directory to save results
    out_dir = os.path.join(PROCESS_OUT_DIR, NAME)
    os.makedirs(out_dir, exist_ok=True)

    output = run_readdy_simple_process()


if __name__ == '__main__':
    main()
