from typing import Any, Dict

from vivarium.core.emitter import Emitter

import numpy as np
import pandas as pd
from simulariumio import (
    TrajectoryConverter,
    TrajectoryData,
    AgentData,
    MetaData,
    UnitData,
)


class SimulariumEmitter(Emitter):
    def __init__(self, config: Dict[str, str]) -> None:
        super().__init__(config)
        self.configuration_data = None
        self.saved_data: Dict[float, Dict[str, Any]] = {}

    def emit(self, data: Dict[str, Any]) -> None:
        """
        Emit the timeseries history portion of ``data``, which is
        ``data['data'] if data['table'] == 'history'`` and put it at
        ``data['data']['time']`` in the history.
        """
        if data["table"] == "configuration":
            self.configuration_data = data["data"]
            assert "processes" in self.configuration_data, "please emit processes"
        if data["table"] == "history":
            emit_data = data["data"]
            time = emit_data["time"]
            self.saved_data[time] = {
                key: value for key, value in emit_data.items() if key not in ["time"]
            }

    def get_simularium_fibers(self, time, fibers, actin_radius, trajectory):
        """
        Shape fiber state data into Simularium fiber agents
        """
        n_agents = 0
        time_index = len(trajectory["times"])
        trajectory["times"].append(time)
        trajectory["unique_ids"].append([])
        trajectory["type_names"].append([])
        trajectory["n_subpoints"].append([])
        trajectory["subpoints"].append([])
        for fiber_id in fibers:
            fiber = fibers[fiber_id]
            n_agents += 1
            trajectory["unique_ids"][time_index].append(int(fiber_id))
            trajectory["type_names"][time_index].append(fiber["type_name"])
            trajectory["n_subpoints"][time_index].append(len(fiber["points"]))
            trajectory["subpoints"][time_index].append(fiber["points"])
        trajectory["n_agents"].append(n_agents)
        trajectory["viz_types"].append(n_agents * [1001.0])
        trajectory["positions"].append(n_agents * [[0.0, 0.0, 0.0]])
        trajectory["radii"].append(n_agents * [actin_radius])
        return trajectory

    def get_simularium_monomers(self, time, monomers, actin_radius, trajectory):
        """
        Shape monomer state data into Simularium agents
        """
        time_index = len(trajectory["times"])
        trajectory["times"].append(time)
        trajectory["unique_ids"].append([])
        trajectory["type_names"].append([])
        trajectory["positions"].append([])
        edge_ids = []
        edge_positions = []
        for particle_id in monomers["particles"]:
            particle = monomers["particles"][particle_id]
            trajectory["unique_ids"][time_index].append(int(particle_id))
            trajectory["type_names"][time_index].append(particle["type_name"])
            trajectory["positions"][time_index].append(np.array(particle["position"]))
            # visualize edges between particles
            for neighbor_id in particle["neighbor_ids"]:
                neighbor_id_str = str(neighbor_id)
                edge = (particle_id, neighbor_id_str)
                reverse_edge = (
                    neighbor_id_str,
                    particle_id,
                )
                if edge not in edge_ids and reverse_edge not in edge_ids:
                    edge_ids.append(edge)
                    edge_positions.append(
                        [
                            np.array(particle["position"]),
                            np.array(
                                monomers["particles"][neighbor_id_str]["position"]
                            ),
                        ]
                    )
        n_agents = len(trajectory["unique_ids"][time_index])
        n_edges = len(edge_ids)
        trajectory["n_agents"].append(n_agents + n_edges)
        trajectory["viz_types"].append(n_agents * [1000.0])
        trajectory["viz_types"][time_index] += n_edges * [1001.0]
        trajectory["unique_ids"][time_index] += [1000 + i for i in range(n_edges)]
        trajectory["type_names"][time_index] += ["edge" for edge in range(n_edges)]
        trajectory["positions"][time_index] += n_edges * [[0.0, 0.0, 0.0]]
        trajectory["radii"].append(n_agents * [actin_radius])
        trajectory["radii"][time_index] += n_edges * [1.0]
        trajectory["n_subpoints"].append(n_agents * [0])
        trajectory["n_subpoints"][time_index] += n_edges * [2]
        trajectory["subpoints"].append(n_agents * [2 * [[0.0, 0.0, 0.0]]])
        trajectory["subpoints"][time_index] += edge_positions
        return trajectory

    @staticmethod
    def get_scaled_agent_data(trajectory, scale_factor) -> AgentData:
        """
        Build AgentData object, scaling appropriate values by scale_factor
        """
        return AgentData(
            times=trajectory["times"],
            n_agents=trajectory["n_agents"],
            viz_types=trajectory["viz_types"],
            unique_ids=trajectory["unique_ids"],
            types=trajectory["type_names"],
            positions=[
                [[k * scale_factor for k in j] for j in i]
                for i in trajectory["positions"]
            ],
            radii=[[j * scale_factor for j in i] for i in trajectory["radii"]],
            n_subpoints=trajectory["n_subpoints"],
            subpoints=[
                [[k * scale_factor for k in j] for j in i]
                for i in trajectory["subpoints"]
            ],
        )

    @staticmethod
    def get_simularium_converter(
        trajectory, box_dimensions, scale_factor
    ) -> TrajectoryConverter:
        """
        Shape a dictionary of jagged lists into a Simularium TrajectoryData object
        and provide it to a TrajectoryConverter for conversion
        """
        spatial_units = UnitData("nm")
        spatial_units.multiply(1 / scale_factor)
        return TrajectoryConverter(
            TrajectoryData(
                meta_data=MetaData(
                    box_size=scale_factor * box_dimensions,
                ),
                agent_data=SimulariumEmitter.get_scaled_agent_data(
                    trajectory, scale_factor
                ),
                time_units=UnitData("count"),
                spatial_units=spatial_units,
            )
        )

    @staticmethod
    def get_active_simulator(choices) -> str:
        """
        Use choices from state to determine which simulator ran
        """
        medyan_active = "medyan_active" in choices and choices["medyan_active"]
        readdy_active = "readdy_active" in choices and choices["readdy_active"]
        cytosim_active = "cytosim_active" in choices and choices["cytosim_active"]

        if medyan_active and not readdy_active and not cytosim_active:
            return "medyan"
        elif readdy_active and not medyan_active and not cytosim_active:
            return "readdy"
        elif cytosim_active and not medyan_active and not readdy_active:
            return "cytosim"

    def get_data(self) -> dict:
        """
        Save the accumulated timeseries history of "emitted" data to file
        """
        if "readdy_actin" in self.configuration_data:
            actin_radius = self.configuration_data["readdy_actin"]["actin_radius"]
        else:
            actin_radius = 3.0  # TODO add to MEDYAN config
        box_dimensions = None
        trajectory = {
            "times": [],
            "n_agents": [],
            "viz_types": [],
            "unique_ids": [],
            "type_names": [],
            "positions": [],
            "radii": [],
            "n_subpoints": [],
            "subpoints": [],
        }
        times = list(self.saved_data.keys())
        times.sort()
        vizualize_time_index = 0
        for time, state in self.saved_data.items():
            print(f"time = {time}")
            index = times.index(time)
            prev_simulator = "none"
            if index > 0:
                prev_simulator = SimulariumEmitter.get_active_simulator(
                    self.saved_data[times[index - 1]]["choices"]
                )
            current_simulator = SimulariumEmitter.get_active_simulator(state["choices"])
            print(f"prev_simulator = {prev_simulator}")
            print(f"current_simulator = {current_simulator}")
            """visualize the first frame in the simulator that started first
            then subsequent frames according the the simulator that ran 
            right before that time point"""
            if prev_simulator == "none":
                if current_simulator == "medyan" or current_simulator == "cytosim":
                    print(f"  visualize current {current_simulator}")
                    if box_dimensions is None:
                        box_dimensions = np.array(state["fibers_box_extent"])
                    trajectory = self.get_simularium_fibers(
                        vizualize_time_index,
                        state["fibers"],
                        actin_radius,
                        trajectory,
                    )
                    vizualize_time_index += 1
                if current_simulator == "readdy":
                    print("  visualize current readdy")
                    trajectory = self.get_simularium_monomers(
                        vizualize_time_index,
                        state["monomers"],
                        actin_radius,
                        trajectory,
                    )
                    vizualize_time_index += 1
            elif prev_simulator == "medyan" or prev_simulator == "cytosim":
                print(f"  visualize previous {prev_simulator}")
                if box_dimensions is None:
                    box_dimensions = np.array(state["fibers_box_extent"])
                trajectory = self.get_simularium_fibers(
                    vizualize_time_index,
                    state["fibers"],
                    actin_radius,
                    trajectory,
                )
                vizualize_time_index += 1
            elif prev_simulator == "readdy":
                print("  visualize readdy")
                trajectory = self.get_simularium_monomers(
                    vizualize_time_index,
                    state["monomers"],
                    actin_radius,
                    trajectory,
                )
                vizualize_time_index += 1
        simularium_converter = SimulariumEmitter.get_simularium_converter(
            trajectory, box_dimensions, 0.1
        )
        simularium_converter.save("out/actin_test")
