from vivarium.core.composer import Composer
from vivarium.core.engine import Engine
from vivarium.processes.alternator import PeriodicEvent

from vivarium_cytosim import CytosimProcess
from vivarium_models.data.fibers import single_fiber

from vivarium.core.process import Step

import numpy as np
import copy

READDY_TIMESTEP = 0.0000001
ALTERNATOR_PERIODS = [2.0, READDY_TIMESTEP]


class AnchorMover(Step):
    defaults = {
        "fiber_id": 0,
        "point_index": 0,
        "movement_vector": [0, 0, 0],
    }

    def __init__(self, config=None):
        super().__init__(config)

    def ports_schema(self):
        return {
            "fibers": {
                "*": {
                    "type_name": {
                        "_default": "",
                        "_updater": "set",
                        "_emit": True,
                    },
                    "points": {
                        "_default": [],
                        "_updater": "set",
                        "_emit": True,
                    },
                }
            }
        }

    def next_update(self, timestep, state):
        points = state["fibers"][self.parameters["fiber_id"]]["points"]
        anchor = points[self.parameters["point_index"]]
        anchor_moved = anchor + np.array(self.parameters["movement_vector"])
        points[self.parameters["point_index"]] = anchor_moved

        return {"fibers": {self.parameters["fiber_id"]: {"points": points}}}


class AnchorMoverCytosim(CytosimProcess):
    new_defaults = {
        "fiber_id": 0,
        "point_index": 0,
        "movement_vector": [0, 0, 0],
    }

    def __init__(self, config=None):
        parameters = copy.deepcopy(self.new_defaults)
        parameters.update(config)
        super().__init__(parameters)

    def next_update(self, timestep, state):
        points = state["fibers"][self.parameters["fiber_id"]]["points"]
        anchor = points[self.parameters["point_index"]]
        anchor_moved = anchor + np.array(self.parameters["movement_vector"])
        points[self.parameters["point_index"]] = anchor_moved
        update = super().next_update(timestep, state)
        return update


class BucklingSqueeze(Composer):
    defaults = {
        "periodic_event": {"periods": [1.0]},
        "cytosim_anchor_mover_squeeze": {
            "model_name": "buckling_squeeze",
            "movement_vector": [5, 0, 0],
            "fiber_id": "1",
        },
        # "cytosim_squeeze": {
        #     'model_name': 'buckling_squeeze'
        # },
        # "anchor_mover": {
        #     "movement_vector": [0, 5, 0],
        #     "fiber_id": "1",
        # }
    }

    def __init__(self, config=None):
        super().__init__(config)

    def generate_processes(self, config):
        periodic_event = PeriodicEvent(config["periodic_event"])
        # cytosim_squeeze = CytosimProcess(config['cytosim_squeeze'])
        # anchor_mover = AnchorMover(config["anchor_mover"])
        cytosim_anchor_mover_squeeze = AnchorMoverCytosim(
            config["cytosim_anchor_mover_squeeze"]
        )

        return {
            "periodic_event": periodic_event,
            # 'cytosim_squeeze': cytosim_squeeze,
            # "anchor_mover": anchor_mover,
            "cytosim_anchor_mover_squeeze": cytosim_anchor_mover_squeeze,
        }

    def generate_topology(self, config):
        return {
            "periodic_event": {
                "event_trigger": ("alternate_trigger",),
                "period_index": ("period_index",),
            },
            # "cytosim_squeeze": {
            #     "fibers": ("fibers",),
            #     "fibers_box_extent": ("fibers_box_extent",),
            # },
            # "anchor_mover": {
            #     "fibers": ("fibers",),
            # }
            "cytosim_anchor_mover_squeeze": {
                "fibers": ("fibers",),
                "fibers_box_extent": ("fibers_box_extent",),
            },
        }


def run_buckling_squeeze():
    initial_state = single_fiber()
    initial_state["choices"] = "N/A"
    cytosim_config = {
        "actin_segmentation": 0.005,
        "timestep": 5,
        "template_directory": "vivarium_models/templates/",
    }
    buckling_squeeze_config = {
        # "cytosim_squeeze": cytosim_config
        "cytosim_anchor_mover_squeeze": cytosim_config
    }
    buckling_squeeze = BucklingSqueeze(buckling_squeeze_config)
    composite = buckling_squeeze.generate()
    composite["initial_state"] = initial_state
    engine = Engine(
        processes=composite["processes"],
        topology=composite["topology"],
        initial_state=composite["initial_state"],
        emitter="simularium",
        emit_processes=True,
    )
    engine.update(100)
    return engine.emitter.get_data()


if __name__ == "__main__":
    run_buckling_squeeze()
