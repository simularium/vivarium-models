import numpy as np

from vivarium.core.process import Process
from vivarium.core.engine import Engine
from vivarium.core.control import run_library_cli

from tqdm import tqdm
from simularium_readdy_models.actin import (
    ActinSimulation,
    ActinUtil,
    ActinTestData,
    ActinAnalyzer,
)
from simularium_readdy_models import ReaddyUtil
from vivarium_models.util import create_monomer_update, format_monomer_results
from vivarium_models.library.scan import Scan

NAME = "ReaDDy_actin"

test_monomer_data = {
    "monomers": {
        "box_center": np.array([1000.0, 0.0, 0.0]),
        "box_size": 500.0,
        "topologies": {
            1: {
                "type_name": "Arp23-Dimer",
                "particle_ids": [1, 2],
            },
            0: {
                "type_name": "Actin-Monomer",
                "particle_ids": [0],
            },
        },
        "particles": {
            0: {
                "type_name": "actin#free_ATP",
                "position": np.array([1002, 0, 0]),
                "neighbor_ids": [],
            },
            1: {
                "type_name": "arp2",
                "position": np.array([1000, 0, 0]),
                "neighbor_ids": [2],
            },
            2: {
                "type_name": "arp3#ATP",
                "position": np.array([1000, 0, 4]),
                "neighbor_ids": [1],
            },
        },
    }
}


class ReaddyActinProcess(Process):
    """
    This process uses ReaDDy to model the dynamics
    of branched actin networks made of spatially explicit monomers
    """

    name = NAME

    defaults = ActinUtil.DEFAULT_PARAMETERS

    def __init__(self, parameters=None):
        super(ReaddyActinProcess, self).__init__(parameters)
        actin_simulation = ActinSimulation(self.parameters)
        self.readdy_system = actin_simulation.system
        self.readdy_simulation = actin_simulation.simulation

    def ports_schema(self):
        return {
            "monomers": {
                "box_center": {
                    "_default": np.array([1000.0, 0.0, 0.0]),
                    "_updater": "set",
                    "_emit": True,
                },
                "box_size": {
                    "_default": 500.0,
                    "_updater": "set",
                    "_emit": True,
                },
                "topologies": {
                    "*": {
                        "type_name": {
                            "_default": "",
                            "_updater": "set",
                            "_emit": True,
                        },
                        "particle_ids": {
                            "_default": [],
                            "_updater": "set",
                            "_emit": True,
                        },
                    }
                },
                "particles": {
                    "*": {
                        "type_name": {
                            "_default": "",
                            "_updater": "set",
                            "_emit": True,
                        },
                        "position": {
                            "_default": np.zeros(3),
                            "_updater": "set",
                            "_emit": True,
                        },
                        "neighbor_ids": {
                            "_default": [],
                            "_updater": "set",
                            "_emit": True,
                        },
                    }
                },
            }
        }

    def initial_state(self, config=None):
        # TODO: make this more general
        return test_monomer_data

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
            n_steps = int(timestep * 1e9 / self.parameters["internal_timestep"])
            for t in tqdm(range(1, n_steps + 1)):
                diffuse()
                update_nl()
                react()
                update_nl()
                calculate_forces()
                observe(t)

        self.readdy_simulation._run_custom_loop(loop, show_summary=False)

    def next_update(self, timestep, states):
        print("in readdy actin process next update")

        ActinUtil.add_monomers_from_data(self.readdy_simulation, states["monomers"])
        self.simulate_readdy(timestep)
        readdy_monomers = ReaddyUtil.get_current_monomers(
            self.readdy_simulation.current_topologies
        )
        transformed_monomers = ReaddyActinProcess._transform_monomers(
            readdy_monomers, states["monomers"]["box_center"]
        )

        return create_monomer_update(states["monomers"], transformed_monomers)

    @staticmethod
    def _transform_monomers(monomers, box_center):
        for particle_id in monomers["particles"]:
            monomers["particles"][particle_id]["position"] += box_center
        return monomers

    # functions to configure and run the process
    def run_readdy_actin_process():
        """
        Run a simulation of the process.

        Returns:
            The simulation output.
        """
        engine = Engine(
            **{
                "processes": {"readdy_actin_process": ReaddyActinProcess()},
                "topology": {
                    "readdy_actin_process": {
                        "monomers": ("monomers",),
                    },
                },
                "initial_state": test_monomer_data,
            }
        )
        engine.update(0.000000005)  # 50 steps
        output = engine.emitter.get_data()
        return output


def get_monomer_data():
    monomer_data = ActinTestData.linear_actin_monomers()
    monomer_data["box_center"] = np.zeros(3)
    monomer_data["box_size"] = 500.0
    return {"monomers": monomer_data}


def run_readdy_actin_process():
    monomer_data = get_monomer_data()
    readdy_actin_process = ReaddyActinProcess()

    engine = Engine(
        **{
            "processes": {"readdy_actin_process": readdy_actin_process},
            "topology": {
                "readdy_actin_process": {
                    "monomers": ("monomers",),
                },
            },
            "initial_state": monomer_data,
        }
    )

    engine.update(0.0000001)  # 1e3 steps
    return engine.emitter.get_data()


def run_scan_readdy():
    monomer_data = get_monomer_data()

    parameters = {
        "1": {
            "parameters": {"actin_concentration": 100.0, "arp23_concentration": 5.0},
            "states": monomer_data,
        },
        "2": {
            "parameters": {"actin_concentration": 200.0, "arp23_concentration": 10.0},
            "states": monomer_data,
        },
        "3": {
            "parameters": {"actin_concentration": 300.0, "arp23_concentration": 20.0},
            "states": monomer_data,
        },
    }

    def count_monomers(results):
        outcome = list(results.values())[-1]
        return len(outcome["monomers"]["particles"])

    def count_monomer_types(results):
        outcome = list(results.values())[-1]
        monomer_types = {}

        for particle in outcome["monomers"]["particles"].values():
            type_name = particle["type_name"]
            if type_name not in monomer_types:
                monomer_types[type_name] = 0
            monomer_types[type_name] += 1

        return monomer_types

    def filament_lengths(results):
        outcome = list(results.values())[-1]
        barbed = None
        pointed = None
        for particle in outcome["monomers"]["particles"].values():
            if "barbed" in particle["type_name"]:
                barbed = np.array(particle["position"])
            elif "pointed" in particle["type_name"]:
                pointed = np.array(particle["position"])

        difference = barbed - pointed
        length = np.linalg.norm(difference)
        return length

    def percent_filamentous_actin(results):
        monomer_data = [list(results.values())[-1]["monomers"]]
        return (
            100.0
            * ActinAnalyzer.analyze_ratio_of_filamentous_to_total_actin(monomer_data)[0]
        )

    def percent_bound_arp23(results):
        monomer_data = [list(results.values())[-1]["monomers"]]
        return (
            100.0 * ActinAnalyzer.analyze_ratio_of_bound_to_total_arp23(monomer_data)[0]
        )

    def percent_daughter_actin(results):
        monomer_data = [list(results.values())[-1]["monomers"]]
        return (
            100.0
            * ActinAnalyzer.analyze_ratio_of_daughter_to_total_actin(monomer_data)[0]
        )

    def mother_filament_lengths(results):
        monomer_data = [list(results.values())[-1]["monomers"]]
        return ActinAnalyzer.analyze_average_over_time(
            ActinAnalyzer.analyze_mother_filament_lengths(monomer_data)
        )[0]

    def daughter_filament_lengths(results):
        monomer_data = [list(results.values())[-1]["monomers"]]
        return ActinAnalyzer.analyze_daughter_filament_lengths(monomer_data)[0]

    def branch_angles(results):
        box_size = list(results.values())[-1]["monomers"]["box_size"]
        monomer_data = [list(results.values())[-1]["monomers"]]
        periodic_boundary = False  # TODO get from parameters
        return ActinAnalyzer.analyze_branch_angles(
            monomer_data, box_size, periodic_boundary
        )[0]

    def short_helix_pitches(results):
        monomer_data = format_monomer_results(results)
        periodic_boundary = False  # TODO get from parameters
        return ActinAnalyzer.analyze_short_helix_pitches(
            monomer_data, monomer_data[0]["box_size"], periodic_boundary
        )

    def long_helix_pitches(results):
        monomer_data = format_monomer_results(results)
        periodic_boundary = False  # TODO get from parameters
        return ActinAnalyzer.analyze_long_helix_pitches(
            monomer_data, monomer_data[0]["box_size"], periodic_boundary
        )

    def filament_straightness(results):
        monomer_data = format_monomer_results(results)
        periodic_boundary = False  # TODO get from parameters
        return ActinAnalyzer.analyze_filament_straightness(
            monomer_data, monomer_data[0]["box_size"], periodic_boundary
        )

    metrics = {
        "count_monomers": count_monomers,
        "count_monomer_types": count_monomer_types,
        "filament_lengths": filament_lengths,
        "percent_filamentous_actin": percent_filamentous_actin,
        "percent_bound_arp23": percent_bound_arp23,
        "percent_daughter_actin": percent_daughter_actin,
        "mother_filament_lengths": mother_filament_lengths,
        "daughter_filament_lengths": daughter_filament_lengths,
        "branch_angles": branch_angles,
        "short_helix_pitches": short_helix_pitches,
        "long_helix_pitches": long_helix_pitches,
        "filament_straightness": filament_straightness,
    }

    scan = Scan(parameters, ReaddyActinProcess, 0.0000001, metrics=metrics)
    results = scan.run_scan()
    return results


library = {"0": run_readdy_actin_process, "1": run_scan_readdy}


if __name__ == "__main__":
    run_library_cli(library)
