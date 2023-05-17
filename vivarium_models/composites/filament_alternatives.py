from vivarium.core.composer import Composer
from vivarium.core.engine import Engine
from vivarium.processes.alternator import Alternator, PeriodicEvent

from vivarium_medyan import MedyanProcess
from vivarium_cytosim import CytosimProcess
from vivarium_models.data.fibers import centered_initial_fibers

ALTERNATOR_PERIODS = [2.0, 2.0]


class FilamentAlternatives(Composer):
    defaults = {
        "periodic_event": {"periods": ALTERNATOR_PERIODS},
        "medyan": {"time_step": 1.0, "_condition": ("choices", "medyan_active")},
        "cytosim": {
            "time_step": 1.0,
            "_condition": ("choices", "cytosim_active"),
            "confine": {"side": "inside", "force": 100, "space": "cell"},
        },
        "alternator": {"choices": ["medyan_active", "cytosim_active"]},
    }

    def __init__(self, config=None):
        super().__init__(config)

    def generate_processes(self, config):
        periodic_event = PeriodicEvent(config["periodic_event"])
        medyan = MedyanProcess(config["medyan"])
        cytosim = CytosimProcess(config["cytosim"])
        alternator = Alternator(config["alternator"])

        return {
            "periodic_event": periodic_event,
            "medyan": medyan,
            "cytosim": cytosim,
            "alternator": alternator,
        }

    def generate_topology(self, config):
        return {
            "periodic_event": {
                "event_trigger": ("alternate_trigger",),
                "period_index": ("period_index",),
            },
            "medyan": {"fibers": ("fibers",)},
            "cytosim": {"fibers": ("fibers",)},
            "alternator": {
                "alternate_trigger": ("alternate_trigger",),
                "choices": {
                    "medyan_active": (
                        "choices",
                        "medyan_active",
                    ),
                    "cytosim_active": (
                        "choices",
                        "cytosim_active",
                    ),
                },
            },
        }


def run_filament_alternatives():
    initial_state = centered_initial_fibers()
    initial_state["choices"] = {"medyan_active": False, "cytosim_active": True}
    medyan_config = {
        "template_directory": "vivarium_models/templates/",
        "transform_points": [2000.0, 1000.0, 1000.0],
        "filament_projection_type": "PREDEFINED",
    }
    cytosim_config = {
        "template_directory": "vivarium_models/templates/",
    }
    filament_alternatives_config = {
        "medyan": medyan_config,
        "cytosim": cytosim_config,
    }
    filament_alternatives = FilamentAlternatives(filament_alternatives_config)
    composite = filament_alternatives.generate()
    composite["initial_state"] = initial_state
    engine = Engine(
        processes=composite["processes"],
        topology=composite["topology"],
        initial_state=composite["initial_state"],
        emitter="simularium",
        emit_processes=True,
    )
    engine.update(6)
    return engine.emitter.get_data()


if __name__ == "__main__":
    run_filament_alternatives()
